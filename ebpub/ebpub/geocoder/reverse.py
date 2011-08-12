#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest
from psycopg2 import Binary
from django.contrib.gis.geos import Point
from django.db import connection

class ReverseGeocodeError(Exception):
    pass

def reverse_geocode(point):
    """
    Looks up the nearest block to the point.

    Argument can be either a Point instance, or an (x, y) tuple, or a
    WKT string.
    """
    # Defer import to avoid cyclical import.
    from ebpub.streets.models import Block

    if isinstance(point, basestring):
        from django.contrib.gis.geos import fromstr
        point = fromstr(point, srid=4326)
    elif isinstance(point, tuple) or isinstance(point, list):
        point = Point(tuple(point))
    # In degrees for now because transforming to a projected space is
    # too slow for this purpose. TODO: store projected versions of the
    # locations alongside the canonical lng/lat versions.
    min_distance = 0.007
    # We use min_distance to cut down on the searchable space, because
    # the distance query we do next that actually compares distances
    # between geometries does not use the spatial index. TODO: convert
    # this to GeoDjango syntax. Should be possible but there are some
    # subtleties / performance issues with the DB API.
    cursor = connection.cursor()
    # Switched to WKT rather than WKB, because constructing WKB as a
    # string leads to psycopg2 getting confused by '%' as per
    # http://stackoverflow.com/questions/1734814/why-isnt-psycopg2-executing-any-of-my-sql-functions-indexerror-tuple-index-ou
    # We could probably do something like
    # str(Binary(point.wkb)).replace('%', '%%') ... but I don't know
    # if that could have other problems?
    # Or maybe a Binary() could be passed as a parameter to cursor.execute().
    # Anyway, WKT is safe.
    params = {'field_list': ', '.join([f.column for f in Block._meta.fields]),
              'pt_wkt': point.wkt,
              'geom_fieldname': 'geom',
              'tablename': Block._meta.db_table,
              'min_distance': min_distance
              }
    sql = """
        SELECT %(field_list)s, ST_Distance(ST_GeomFromText('%(pt_wkt)s', 4326), %(geom_fieldname)s) AS "dist"
        FROM %(tablename)s
        WHERE id IN
            (SELECT id
             FROM %(tablename)s
             WHERE ST_DWithin(%(geom_fieldname)s, ST_GeomFromText('%(pt_wkt)s', 4326), %(min_distance)s))
        ORDER BY "dist"
        LIMIT 1;
    """ % params
    cursor.execute(sql)
    num_fields = len(Block._meta.fields)
    rows = cursor.fetchall()
    if not rows:
        raise ReverseGeocodeError('No results')
    block, distance = [(Block(*row[:num_fields]), row[-1]) for row in rows][0]
    return block, distance

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

"""
Utility functions for working with GeoDjango GDAL and GEOS data


"""

from django.contrib.gis import geos
from django.contrib.gis.geos import Point, LineString, Polygon, GeometryCollection, MultiPoint, MultiLineString, MultiPolygon
from ebpub.metros.allmetros import get_metro
import logging

logger = logging.getLogger('ebpub.utils.geodjango')

def reduce_layer_geom(layer, method):
    """
    Iterates over all the geometries in an GDAL layer and successively
    applies given `method' to the geometries.
    """
    def reduction(x, y):
        return getattr(x, method)(y)
    
    return reduce(reduction, [feat.geom for feat in layer])

# TODO: remove this once line_merge is added to django.contrib.gis.geos
from django.contrib.gis.geos.libgeos import lgeos
from django.contrib.gis.geos.prototypes.topology import topology
geos_linemerge = topology(lgeos.GEOSLineMerge)
def line_merge(geom):
    return geom._topology(geos_linemerge(geom.ptr))

def flatten(geos_geom):
    """
    Flattens a GEOS geometry and returns a list of the component geometries.
    """
    def _flatten(geom, acc):
        if isinstance(geom, (Point, LineString, Polygon)):
            acc.append(geom)
            return acc
        elif isinstance(geom, (GeometryCollection, MultiPoint, MultiLineString, MultiPolygon)):
            subgeom_list = list(geom)
            if subgeom_list:
                acc.append(subgeom_list.pop(0))
                for subgeom in subgeom_list:
                    _flatten(subgeom, acc)
            return acc
        else:
            raise TypeError, 'not a recognized GEOSGeometry type'
    flattened = []
    _flatten(geos_geom, flattened)
    return flattened

def make_geomcoll(geom_list):
    """
    From a list of geometries, return a single GeometryCollection (or
    subclass) geometry.

    This flattens multi-point/linestring/polygon geometries in the
    list.
    """
    flattened = []

    for geom in geom_list:
        flattened.extend(flatten(geom))

    return GeometryCollection(flattened)

def make_multi(geom_list, collapse_single=False):
    """
    Convert a list of Geometries (of the same type) into a single
    Multi(Point|Linestring|Polygon).
    """
    if len(geom_list) == 1 and collapse_single:
        return geom_list[0]

    geom_types = set(g.geom_type for g in geom_list)

    if len(geom_types) > 1:
        raise ValueError, 'all geometries must be of the same geom_type'

    geom_type = geom_types.pop()

    valid_geom_types = ('Point', 'LineString', 'Polygon')

    if geom_type not in valid_geom_types:
        raise ValueError, 'geometries must be of type %s' % ', '.join(valid_geom_types)

    cls = getattr(geos, 'Multi%s' % geom_type)
    return cls(geom_list)


def flatten_geomcollection(geom):
    """
    Workaround for bug #95: if we get a GeometryCollection,
    save it instead as a MultiPolygon, because PostGIS doesn't support
    using Collections for anything useful like
    ST_Intersects(some_other_geometry), so we effectively can't
    use them at all. Yuck.
    """
    if geom.geom_type == 'GeometryCollection':
        geom = make_multi(flatten(geom))
        logger.warn("Got a GeometryCollection. Can't call ST_Intersects() on those."
                    " Munged it into a %s." % geom.geom_type)
    return geom

def smart_transform(geom, srid, clone=True):
    """
    Returns a new geometry transformed to the srid given. Assumes if
    the initial geom is lacking an SRS that it is EPSG 4326. (Hence the
    "smartness" of this function.) This fixes many silent bugs when
    transforming between SRSes when the geometry is missing this info.
    """
    if not geom.srs:
        geom.srid = 4326
    return geom.transform(srid, clone=clone)


def ensure_valid(geom, name=''):
    """Make sure a geometry is valid; if necessary, make a 0.0 buffer
    around it. (This is a well-known hack to fix broken geometries.)
    """
    if not geom.valid:
        geom = geom.buffer(0.0)
        if not geom.valid:
            logger.warn('invalid geometry for %s' % name)
    return geom

def intersects_metro_bbox(geom):
    """
    Return True if the geometry intersects with the bounding box of
    the current metro.
    """
    return geom.intersects(get_default_bounds())


def get_default_bounds():
    """Returns the bounding box of the metro, as a Polygon.

    >>> import mock
    >>> metrodict = {'extent': (-10.0, 15.0, -5.0, 20.0)}
    >>> with mock.patch('ebpub.utils.geodjango.get_metro', lambda: metrodict) as get_metro:
    ...     bounds = get_default_bounds()
    >>> bounds  #doctest: +ELLIPSIS
    <Polygon object at ...>
    >>> bounds.extent
    (-10.0, 15.0, -5.0, 20.0)
    """
    return Polygon.from_bbox(get_metro()['extent'])

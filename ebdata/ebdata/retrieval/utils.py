# -*- coding: utf-8 -*-
#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#


"""
Utilities useful for scraping.
"""

# The convert_entities() function is derived from Copyright © 1995-2008
# Fredrik Lundh. It is used under the terms of the Python-style license
# specified at http://effbot.org/zone/copyright.htm.
# 
# Copyright (c) 1995-2008 by Fredrik Lundh
# 
# By obtaining, using, and/or copying this software and/or its associated
# documentation, you agree that you have read, understood, and will comply
# with the following terms and conditions:
# 
# Permission to use, copy, modify, and distribute this software and its
# associated documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appears in all copies, and that
# both that copyright notice and this permission notice appear in supporting
# documentation, and that the name of Secret Labs AB or the author not be
# used in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission.
# 
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.
# IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.


from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
from ebpub.utils.geodjango import smart_transform
import htmlentitydefs
import logging
import re

logger = logging.getLogger('ebdata.retrieval.utils')

multispace_re = re.compile(r'\s\s+')

def norm_dict_space(d, *keys):
    """
    Replaces 2 or more spaces with a single space, in dict values,
    and strips leading/trailing space.
    (Keys are not changed.)

    >>> d = {'name': '  john  smith ',
    ...      'address': '  123  main st ',
    ...      ' address': ' 123  main st'}
    >>> norm_dict_space(d, 'name', 'address')
    >>> sorted(d.items())
    [(' address', ' 123  main st'), ('address', '123 main st'), ('name', 'john smith')]
    """
    for key in keys:
        d[key] = multispace_re.sub(' ', d[key]).strip()

def obj_dict_merge(obj, update_dict, ignore_attrs=None):
    """Updates the attributes of obj with the values in update_dict.

    Takes a list of attributes to ignore.

    Returns True if any of obj's attributes were updated, False otherwise.
    """
    if not ignore_attrs:
        ignore_attrs = []
    changed = False
    for attr in obj.__dict__.keys():
        if attr not in ignore_attrs and update_dict.has_key(attr):
            update_val = update_dict[attr]
            if getattr(obj, attr) != update_val:
                setattr(obj, attr, update_val)
                changed = True
    return changed, obj

# From http://effbot.org/zone/re-sub.htm#unescape-html
# See copyright at top of this file.

def convert_entities(text):
    """
    Converts HTML entities in the given string (e.g., '&#28;' or '&nbsp;') to
    their corresponding characters.

    Note this does NOT do the same thing as xml.sax.saxutils.unescape();
    for that you'd have to pass in an exhaustive dictionary of
    entity -> replacement pairs.
    """
    NAMED_ENTITY_SPECIAL_CASES = {
        'apos': u"'",
    }
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            entity = text[1:-1]
            try:
                text = unichr(htmlentitydefs.name2codepoint[entity])
            except KeyError:
                try:
                    return NAMED_ENTITY_SPECIAL_CASES[entity]
                except KeyError:
                    pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def locations_are_close(geom_a, geom_b, max_distance=200):
    """
    Verifies that two locations are within a certain distance from
    each other. Returns a tuple of (is_close, distance), where
    is_close is True only if the locations are within max_distance.

    Assumes max_distance is in meters.
    """
    # Both geometries must be GEOSGeometry for the distance method.
    if not (isinstance(geom_a, GEOSGeometry) and isinstance(geom_b, GEOSGeometry)):
        raise ValueError, 'both geometries must be GEOSGeometry instances'
    carto_srid = 3395 # SRS in meters
    geom_a = smart_transform(geom_a, carto_srid)
    geom_b = smart_transform(geom_b, carto_srid)
    distance = geom_a.distance(geom_b)
    return (distance < max_distance), distance


def get_point(record):
    """
    Given a dict, eg. a record as returned by feedparser, tries to
    find either flavor of georss or geo attributes, as well as some
    other common non-standard conventions.

    Returns a Point or None.

    Locations with both lat = 0 and lon = 0 are assumed to be bad; we
    return None for those.
    """
    # This tries to work around feedparser bugs where depending on
    # whether you get a loose or strict parser, you might or might
    # not see the namespace prefix on the attribute name.

    # TODO: support other georss geometry types as per
    # http://www.georss.org/simple ... so far only handles Point.

    # TODO: support xCal geometries
    # https://tools.ietf.org/html/rfc6321#section-3.4.1.2

    if 'gml_pos' in record:
        # Looks like georss gml.
        lat, lon = record['gml_pos'].split()
    elif 'point' in record:
        # Unfortunately, with broken namespace handling, this
        # might be georss_simple or georss gml. Try both.
        if 'where' in record and 'pos' in record:
            # It's GML.
            lat, lon = record['pos'].strip().split()
        else:
            lat, lon = record['point'].strip().split()
    elif 'georss_point' in record:
        # It's georss simple.
        lat, lon = record['georss_point'].strip().split()
    elif 'geo_lat' in record:
        # It's the rdf geo namespace.
        lat, lon = record['geo_lat'], record['geo_lon']
    elif 'lat' in record:
        lat = record['lat']
        # 'lon' = geo with broken namespace handling.
        # The others are non-standard, but I've seen 'lng' in eg.
        # seeclickfix issues json.
        lon = record.get('lng') or record.get('lon') or record.get('long')
        if lon is None:
            logger.debug("Found lat %r, but nothing like a longitude" % lat)
            return None
    elif 'latitude' in record:
        # Another common non-standard convention.
        lat, lon = record['latitude'], record['longitude']
    elif 'xCal_latitude' in record:
        # Looks like xCal.
        # Not sure about capitalization of namespace?
        lat, lon = record['xCal_latitude'], record['xCal_longitude']
    else:
        logger.debug("no known geometry types found in record %s" % record)
        return None
    lat, lon = float(lat), float(lon)
    if (lat, lon) == (0.0, 0.0):
        logger.warn("Ignoring location with bad coordinates (0, 0)")
        return None
    return Point(lon, lat)

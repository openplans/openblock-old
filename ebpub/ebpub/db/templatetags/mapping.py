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

from django import template
from django.conf import settings

def tile_url_list():
    return settings.TILE_URL_LIST

register = template.Library()

@register.inclusion_tag("etc/mapping_includes.html")
def activate_mapping():
    return {
        "city": settings.SHORT_NAME,
        "tile_url_list": tile_url_list()
    }

MAX_MARKER_RADIUS = 18
MIN_MARKER_RADIUS = 3

def _get_marker_radius(normalized_value):
    """
    Assumes `normalized_value` is in the range 0.0 and 1.0
    """
    return int(round(((MAX_MARKER_RADIUS - MIN_MARKER_RADIUS) * normalized_value) + MIN_MARKER_RADIUS))

@register.simple_tag
def get_marker_radius(normalized_value):
    return unicode(_get_marker_radius(normalized_value))

@register.simple_tag
def get_marker_url(normalized_value):
    """
    Returns a URL to a marker who's size is based on a normalized (i.e., between
    0.0 and 1.0) value.
    """
    radius = _get_marker_radius(normalized_value)
    if hasattr(settings, 'MARKER_URL_BASE'):
        return settings.MARKER_URL_BASE + 'marker_%d.png' % radius
    else:
        return '/images/mapmarkers/bubble/marker_%d.png' % radius

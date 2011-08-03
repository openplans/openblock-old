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

register = template.Library()


@register.simple_tag
def map_icon_img(obj):
    """
    Returns an image tag with a URL for a map icon for the given
    object, which may be a db.Schema, or streets.PlaceType.

    (If there's no image configured but there's a fill color, makes a
    little box of the right color.)
    """
    url = getattr(obj, 'map_icon_url', '') or ''
    url = url.strip()
    if url:
        alt = '%s icon' % (obj.name or obj.slug)
        return '<img class="schema-icon" src="%s" alt="%s" />' % (url, alt)
    color = getattr(obj, 'map_color', '') or ''
    color = color.strip()
    if color:
        return '<div class="schema-colorsample" style="background: %s">&nbsp;</div>' % color
    return ''

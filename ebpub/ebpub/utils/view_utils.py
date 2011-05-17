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

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from ebpub.constants import BLOCK_RADIUS_CHOICES
from ebpub.constants import BLOCK_RADIUS_DEFAULT
from ebpub.db.models import Location
from ebpub.db.models import Schema
from ebpub.streets.models import Block


def eb_render(request, *args, **kwargs):
    """
    Replacement for render_to_response that uses RequestContext.
    """
    kwargs['context_instance'] = RequestContext(request)
    return render_to_response(*args, **kwargs)

def parse_pid(pid):
    """
    Returns a tuple of (place, block_radius, xy_radius), where block_radius and
    xy_radius are None for Locations.

    PID examples:
        'b:12.1' (block ID 12, 1-block radius)
        'l:32' (location ID 32)
    """
    try:
        place_type, place_id = pid.split(':')
        if place_type == 'b':
            place_id, block_radius = place_id.split('.')
        place_id = int(place_id)
    except (KeyError, ValueError):
        raise Http404('Invalid place')
    if place_type == 'b':
        try:
            xy_radius = BLOCK_RADIUS_CHOICES[block_radius]
        except KeyError:
            raise Http404('Invalid radius')
        return (get_object_or_404(Block, id=place_id), block_radius, xy_radius)
    elif place_type == 'l':
        return (get_object_or_404(Location, id=place_id), None, None)
    else:
        raise Http404


def make_pid(place, block_radius=None):
    """
    Given a place (either a Location or Block), and an optional
    block_radius (None for Locations), returns a place ID string
    parseable by parse_pid.
    """
    if isinstance(place, Block):
        if block_radius is None:
            block_radius = BLOCK_RADIUS_DEFAULT
        block_radius = int(block_radius)
        return 'b:%d.%d' % (place.id, block_radius)
    elif isinstance(place, Location):
        assert block_radius is None
        return 'l:%d' % place.id
    else:
        raise ValueError("Wrong place type %s, expected Location or Block" % place)


def has_staff_cookie(request):
    return request.COOKIES.get(settings.STAFF_COOKIE_NAME) == settings.STAFF_COOKIE_VALUE

def get_schema_manager(request):
    if has_staff_cookie(request):
        return Schema.objects
    else:
        return Schema.public_objects

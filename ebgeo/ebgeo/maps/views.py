#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebgeo
#
#   ebgeo is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebgeo is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebgeo.  If not, see <http://www.gnu.org/licenses/>.
#

from cStringIO import StringIO
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from ebgeo.maps.mapserver import get_mapserver
from ebgeo.maps.shortcuts import render_tile, render_locator_map, render_location_tile
from ebgeo.maps.markers import make_marker
from ebgeo.maps.cached_image import CachedImageResponse

from ebpub.db.views import url_to_place

class TileResponse(object):
    def __init__(self, tile_bytes):
        self.tile_bytes = tile_bytes

    def __call__(self, extension='png'):
        if self.tile_bytes:
            return HttpResponse(self.tile_bytes, mimetype=('image/%s' % extension))
        else:
            raise Http404

def get_tile(request, version, layername, z, x, y, extension='png'):
    'Returns a map tile in the requested format'
    z, x, y = int(z), int(x), int(y)
    response = TileResponse(render_tile(layername, z, x, y, extension='png'))
    return response(extension)

def locator_map(request, version, city, extension='png'):
    'The 75x75 contextual locator map'
    response = TileResponse(render_locator_map(city))
    return response(extension)

def get_marker(request, radius):
    radius = int(radius)
    stroke_width = 1.0

    # Defaults
    fill_color = '#FF4600'
    stroke_color = '#C32700'
    opacity = 1.0

    if 'opacity' in request.GET:
        try:
            opacity = float(request.GET['opacity'])
        except ValueError:
            raise Http404
        else:
            if not (opacity >= 0.0 and opacity <= 1.0):
                raise Http404

    cache_key = 'marker-%s-%s-%s-%s-%s' % (radius, fill_color, stroke_color,
                                           stroke_width, opacity)
    def get_marker_bytes():
        img = make_marker(radius, fill_color, stroke_color, stroke_width, opacity)
        img_sio = StringIO()
        img.save(img_sio, 'PNG')
        return img_sio.getvalue()

    return CachedImageResponse(cache_key, get_marker_bytes)

def get_place_tile(request, *args, **kwargs):
    zoom = int(request.GET.get('zoom', settings.TILECACHE_ZOOM))
    layer = request.GET.get('layer', settings.TILECACHE_LAYER)
    version = request.GET.get('version', settings.TILECACHE_VERSION)
    extension = request.GET.get('extension', settings.TILECACHE_EXTENSION)

    place = url_to_place(*args, **kwargs)
    tile = render_location_tile(place, zoom=zoom, version=version, 
        layer=layer, extension=extension)
    return HttpResponse(tile[1], mimetype=(tile[0]))

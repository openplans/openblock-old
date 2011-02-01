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

from django.http import HttpResponse
from django.core.cache import cache

def set_cache_raw(key, data, timeout=None):
    """
    Works around a Django bug that tries to typecast a regular
    byte string as a Unicode string.
    """
    cache.set(key, (data,), timeout)

def get_cache_raw(key):
    """
    Corresponding `get` function to the `raw_cache_set` workaround
    """
    data = cache.get(key)
    if data is not None:
        return data[0]

class CachedImageResponse(HttpResponse):
    def __init__(self, key, image_gen_fn, expiry_seconds=None, mimetype='image/png'):

        img_bytes = get_cache_raw(key)

        if img_bytes is None:
            img_bytes = image_gen_fn()
            set_cache_raw(key, img_bytes, expiry_seconds)
        
        super(CachedImageResponse, self).__init__(content=img_bytes,
                                                  mimetype=mimetype)

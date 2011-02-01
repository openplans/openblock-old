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

from django.conf.urls.defaults import *
from ebgeo.maps import views
from ebgeo.maps.tilecache_service import request_pat as tile_request_pat

from ebpub.db.constants import BLOCK_URL_REGEX

urlpatterns = patterns('',
#    (r'^tile%s' % tile_request_pat, views.get_tile),
#    (r'^locator/(?P<version>\d+\.\d+)/(?P<city>\w{1,32})\.(?P<extension>(?:png|jpg|gif))$', views.locator_map),
    #(r'^browser/export_pdf/$', views.export_pdf),
#    (r'^marker_(?P<radius>\d{1,2})\.png$', views.get_marker),
    
    (r'^tile/()([-a-z0-9]{1,64})/%s/$' % BLOCK_URL_REGEX, 
        views.get_place_tile, {'place_type': 'block', 'detail_page': True}),
    
)

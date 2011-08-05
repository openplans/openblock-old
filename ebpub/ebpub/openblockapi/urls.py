#   Copyright 2011 OpenPlans and contributors
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

from django.conf.urls.defaults import patterns, url, handler404, handler500
from ebpub.openblockapi import views

urlpatterns = patterns(
    '',
    url(r'^$', views.check_api_available, name="check_api_available"),
    url(r'^geocode/$', views.geocode, name='geocoder_api'),
    url(r'^items.json$', views.items_json, name="items_json"),
    url(r'^items.atom$', views.items_atom, name="items_atom"),
    url(r'^items/types.json$', views.list_types_json, name="list_types_json"),
    url(r'^items/(?P<id_>\d+).json$', views.single_item_json, name="single_item_json"),
    url(r'^items/$', views.items_index, name="items_index"),
    url(r'^locations.json$', views.locations_json, name="locations_json"),
    url(r'^locations/types.json', views.location_types_json, name="location_types_json"),
    url(r'^locations/(?P<loctype>[^/].*)/(?P<slug>.*).json$', views.location_detail_json, name="location_detail_json"),
    url(r'^places/types.json', views.place_types_json, name="place_types_json"),
    url(r'^places/(?P<placetype>[^/].*).json$', views.place_detail_json, name="place_detail_json"),
)

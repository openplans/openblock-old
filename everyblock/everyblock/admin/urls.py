#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of everyblock
#
#   everyblock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   everyblock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with everyblock.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from everyblock.utils.redirecter import redirecter
import views # relative import

urlpatterns = patterns('',
    (r'^$', direct_to_template, {'template': 'admin/index.html'}),
    (r'^schemas/$', views.schema_list),
    (r'^schemas/(\d{1,6})/$', views.edit_schema),
    (r'^schemas/(\d{1,6})/lookups/(\d{1,6})/$', views.edit_schema_lookups),
    (r'^schemafields/$', views.schemafield_list),
    (r'^sources/$', views.blob_seed_list),
    (r'^sources/add/$', views.add_blob_seed),
    (r'^scraper-history/$', views.scraper_history_list),
    (r'^scraper-history/([-\w]{4,32})/$', views.scraper_history_schema),
    (r'^set-staff-cookie/$', views.set_staff_cookie),
    (r'^newsitems/(\d{1,6})/$', views.newsitem_details),
    (r'^geocoder-success-rates/$', views.geocoder_success_rates),
)

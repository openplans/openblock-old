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

from django.conf.urls.defaults import patterns, handler404, handler500
from django.views.generic import list_detail
from ebpub.metros import views
from ebpub.metros.models import Metro

urlpatterns = patterns('',
    (r'^$', list_detail.object_list, {'queryset': Metro.objects.order_by('name'), 'template_object_name': 'metro'}),
    (r'^lookup/$', views.lookup_metro),
)

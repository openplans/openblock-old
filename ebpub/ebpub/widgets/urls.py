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
#

from django.conf.urls.defaults import *
from ebpub.widgets import views

urlpatterns = patterns(
    '',
    url(r'admin\/?$', views.widget_admin_list, name="widget_admin_root"),
    url(r'admin/(?P<slug>[-_a-z0-9]{1,32})\/?$', views.widget_admin, name="widget_admin"),
    url(r'admin/raw_items/(?P<slug>[-_a-z0-9]{1,32})\/?$', views.ajax_widget_raw_items,
        name="ajax_widget_raw_items"),
    url(r'admin/pins/(?P<slug>[-_a-z0-9]{1,32})\/?$', views.ajax_widget_pins,
        name="ajax_widget_pins"),
    url(r'(?P<slug>[-_a-z0-9]{1,32})\.js\/?$', views.widget_javascript,
        name="widget_javascript"),
    url(r'(?P<slug>[-_a-z0-9]{1,32})\/?$', views.widget_content, name="widget_content"),
)

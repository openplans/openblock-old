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

from django.conf.urls.defaults import *
from ebpub.savedplaces import views as savedplaces_views
from ebpub.preferences import views as preferences_views
import views # relative import

urlpatterns = patterns('',
    (r'^dashboard/$', views.dashboard),
    (r'^login/$', views.login),
    (r'^logout/$', views.logout),
    (r'^register/$', views.register),
    (r'^password-change/$', views.request_password_change),
    (r'^email-sent/$', 'django.views.generic.simple.direct_to_template', {'template': 'accounts/email_sent.html'}),
    (r'^saved-places/add/$', savedplaces_views.ajax_save_place),
    (r'^saved-places/delete/$', savedplaces_views.ajax_remove_place),
    (r'^hidden-schemas/add/$', preferences_views.ajax_save_hidden_schema),
    (r'^hidden-schemas/delete/$', preferences_views.ajax_remove_hidden_schema),
    (r'^api/saved-places/$', savedplaces_views.json_saved_places),
    (r'^c/$', views.confirm_email),
    (r'^r/$', views.password_reset),
)

#   Copyright 2011 OpenPlans, and contributors
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

from django.conf.urls.defaults import patterns, url
from ebpub.neighbornews import views

urlpatterns = patterns(
    '',
    url(r'^message/new/$', views.new_message, name="new_message"),
    url(r'^message/(?P<newsitem>.+)/edit/$', views.edit_message, name="edit_message"),
    url(r'^message/(?P<newsitem>.+)/delete/$', views.delete_message, name="delete_message"),

    url(r'^event/new/$', views.new_event, name="new_event"),
    url(r'^event/(?P<newsitem>.+)/edit/$', views.edit_event, name="edit_event"),
    url(r'^event/(?P<newsitem>.+)/delete/$', views.delete_event, name="delete_event"),

    url(r'^by_user/(?P<userid>.+)/$', views.news_by_user, name="neighbornews_by_user"),

)

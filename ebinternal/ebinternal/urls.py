#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebinternal
#
#   ebinternal is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebinternal is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebinternal.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import simple
from ebinternal.citypoll import views as citypoll_views
from ebinternal.feedback import views as feedback_views
from everyblock.utils.redirecter import redirecter

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^(?P<path>(?:images|scripts|styles|openlayers).*)$', 'django.views.static.serve', {'document_root': settings.EB_MEDIA_ROOT}),
    )
else:
    urlpatterns = patterns('')

urlpatterns += patterns('',
    (r'^$', simple.direct_to_template, {'template': 'homepage.html'}),
    (r'^feedback/$', feedback_views.feedback_list),
    (r'^feedback/(\d{1,5})/$', feedback_views.feedback_detail),
    (r'^feedback/change-category/$', feedback_views.feedback_change_category),
    (r'^feedback/ignore/$', feedback_views.feedback_ignore),

    (r'^r/$', redirecter),

    (r'^citypoll/$', citypoll_views.city_vote_list),
    (r'^citypoll/(\d{1,5})/$', citypoll_views.city_detail),

    # This is public (not password-protected via auth).
    (r'^send-feedback/$', feedback_views.save_feedback),
    (r'^send-feedback/city/$', citypoll_views.save_feedback),
)

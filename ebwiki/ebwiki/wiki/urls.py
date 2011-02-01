#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebwiki
#
#   ebwiki is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebwiki is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebwiki.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.syndication.views import feed
from ebwiki.wiki.feeds import LatestEdits
import views # relative import

feeds = {
    'latest': LatestEdits
}

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^(?P<path>styles.*)$', 'django.views.static.serve', {'document_root': settings.WIKI_DOC_ROOT}),
    )
else:
    urlpatterns = patterns('')

urlpatterns += patterns('',
    (r'^$', views.view_page, {'slug': 'index'}),
    (r'^r/$', views.redirecter),
    (r'^latest-changes/$', views.latest_changes),
    (r'^orphans/$', views.list_orphans),

    (r'^(\w{1,30})/$', views.view_page),
    (r'^(\w{1,30})/edit/$', views.edit_page),
    (r'^(\w{1,30})/history/$', views.history),
    (r'^(\w{1,30})/history/(\d{1,6})/$', views.view_version),
    (r'^(\w{1,30})/history/(\d{1,6})/diff/$', views.previous_version_diff),
    (r'^feeds/(?P<url>.*)/$', feed, {'feed_dict': feeds}),
)

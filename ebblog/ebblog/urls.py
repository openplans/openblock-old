#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebblog
#
#   ebblog is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebblog is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebblog.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf.urls.defaults import *
from django.contrib.syndication.views import feed as feed_view
from django.views.generic import date_based, list_detail
from django.contrib import admin
from ebblog.blog.models import Entry
from ebblog.blog import feeds

admin.autodiscover()

info_dict = {
    'queryset': Entry.objects.order_by('pub_date'),
    'date_field': 'pub_date',
}

FEEDS = {
    'rss': feeds.BlogEntryFeed,
}

urlpatterns = patterns('',
    (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>\w+)/$', date_based.object_detail, dict(info_dict, slug_field='slug')),
    (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', date_based.archive_day, info_dict),
    (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', date_based.archive_month, info_dict),
    (r'^(?P<year>\d{4})/$', date_based.archive_year, info_dict),
    (r'^(rss)/$', feed_view, {'feed_dict': FEEDS}),
    (r'^archives/', list_detail.object_list, {'queryset': Entry.objects.order_by('-pub_date'), 'template_name': 'blog/archive.html'}),
    (r'^$', date_based.archive_index, dict(info_dict, template_name='homepage.html')),
    ('^admin/', include(admin.site.urls)),
)

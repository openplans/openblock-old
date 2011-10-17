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

from django.conf import settings
from django.conf.urls.defaults import patterns, url, include, handler404, handler500
from ebpub.alerts import views as alert_views
from ebpub.db import feeds, views
from ebpub.db.constants import BLOCK_URL_REGEX
from ebpub.petitions import views as petition_views
from ebpub.metros.allmetros import get_metro


if settings.DEBUG:
    # This stuff can probably go away if/when we switch to Django 1.3,
    # not sure yet how that interacts with django-static.
    import olwidget
    import os
    olwidget_media_path=os.path.join(
        os.path.abspath(os.path.dirname(olwidget.__file__)), 'static')

    urlpatterns = patterns('',
        (r'^(?P<path>(?:olwidget).*)$',
         'django.views.static.serve', {'document_root': olwidget_media_path}),
        (r'^(?P<path>(?:%s).*)$' % settings.DJANGO_STATIC_NAME_PREFIX.strip('/'),
         'django.views.static.serve', {'document_root': settings.EB_MEDIA_ROOT}),
        (r'^(?P<path>(?:images|scripts|styles|openlayers).*)$', 'django.views.static.serve', {'document_root': settings.EB_MEDIA_ROOT}),
        (r'^(?P<path>(?:%s).*)$' % settings.DJANGO_STATIC_NAME_PREFIX.strip('/'),
         'django.views.static.serve', {'document_root': settings.EB_MEDIA_ROOT}),
    )
else:
    urlpatterns = patterns('')

urlpatterns += patterns('',
    url(r'^$', views.homepage, name="ebpub-homepage"),
    url(r'^search/$', views.search, name='ebpub-search'),
    (r'^news/$', views.schema_list),
    url(r'^locations/$', views.location_type_list, name='ebpub-loc-type-list'),
    url(r'^locations/([-_a-z0-9]{1,32})/$', views.location_type_detail, name='ebpub-loc-type-detail'),
    url(r'^locations/([-_a-z0-9]{1,32})/([-_a-z0-9]{1,32})/$', views.place_detail_timeline, {'place_type': 'location', 'show_upcoming': False}, name="ebpub-location-recent"),
    url(r'^locations/([-_a-z0-9]{1,32})/([-_a-z0-9]{1,32})/upcoming/$', views.place_detail_timeline, {'place_type': 'location', 'show_upcoming': True}, name="ebpub-location-upcoming"),
    url(r'^locations/([-_a-z0-9]{1,32})/([-_a-z0-9]{1,32})/overview/$', views.place_detail_overview, {'place_type': 'location'}, name="ebpub-location-overview"),
    url(r'^locations/([-_a-z0-9]{1,32})/([-_a-z0-9]{1,32})/feeds/$', views.feed_signup, {'place_type': 'location'}, name='ebpub-feed-signup'),
    url(r'^locations/([-_a-z0-9]{1,32})/([-_a-z0-9]{1,32})/alerts/$', alert_views.signup, {'place_type': 'location'}, name='ebpub-location-alerts'),
    (r'^locations/([-a-z0-9]{1,32})/([-a-z0-9]{1,32})/place.kml$', views.place_kml, {'place_type': 'location'}),

    url(r'^rss/locations/([-a-z0-9]{1,32})/([-a-z0-9]{1,32})/$', feeds.LocationFeed(), name='ebpub-location-rss'),

    (r'^accounts/apikeys/', include('ebpub.openblockapi.apikey.urls')),

    (r'^accounts/', include('ebpub.accounts.urls')),

    (r'^alerts/unsubscribe/(\d{1,10})/$', alert_views.unsubscribe),
    (r'^petitions/([-\w]{4,32})/$', petition_views.form_view, {'is_schema': False}),
    (r'^petitions/([-\w]{4,32})/thanks/$', petition_views.form_thanks, {'is_schema': False}),
    url(r'^place-lookup-chart/$', views.ajax_place_lookup_chart, name='ajax-place-lookup-chart'),
    url(r'^place-date-chart/$', views.ajax_place_date_chart, name='ajax-place-date-chart'),
    url(r'^newsitems.geojson/$', views.newsitems_geojson, name='ajax-newsitems-geojson'),
    (r'^api/dev1/', include('ebpub.openblockapi.urls')),
    (r'^widgets/', include('ebpub.widgets.urls')),
    (r'^maps/', include('ebpub.richmaps.urls')),
    (r'^neighbornews/', include('ebpub.neighbornews.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
)

if get_metro()['multiple_cities']:
    # multi-city block patterns.
    urlpatterns += patterns(
        '',
        url(r'^streets/$', views.city_list, name='ebpub-city-list'),
        url(r'^streets/([-a-z]{3,40})/$', views.street_list, name='ebpub-street-list'),
        url(r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/$', views.block_list,
            name='ebpub-block-list'),
        url(r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/%s/$' % BLOCK_URL_REGEX,
            views.place_detail_timeline, {'place_type': 'block', 'show_upcoming': False},
            name='ebpub-block-recent'),
        url(r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/%s/upcoming/$' % BLOCK_URL_REGEX,
            views.place_detail_timeline, {'place_type': 'block', 'show_upcoming': True},
            name='ebpub-block-upcoming'),
        url(r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/%s/overview/$' % BLOCK_URL_REGEX,
            views.place_detail_overview, {'place_type': 'block'},
            name='ebpub-block-overview'),
        url(r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/%s/feeds/$' % BLOCK_URL_REGEX,
            views.feed_signup, {'place_type': 'block'},
            name='ebpub-block-feed-signup'),
        url(r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/%s/alerts/$' % BLOCK_URL_REGEX,
            alert_views.signup, {'place_type': 'block'},
            name='ebpub-block-alerts-signup'),
        url(r'^rss/streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/%s/$' % BLOCK_URL_REGEX,
            feeds.BlockFeed(),
            name='ebpub-block-rss'),
        )
else:
    # single-city block patterns.
    urlpatterns += patterns(
        '',
        url(r'^streets/(\w{0})$', views.street_list,
            name='ebpub-street-list'),
        url(r'^streets/(\w{0})([-a-z0-9]{1,64})/$', views.block_list,
            name='ebpub-block-list'),
        url(r'^streets/(\w{0})([-a-z0-9]{1,64})/%s/$' % BLOCK_URL_REGEX,
            views.place_detail_timeline, {'place_type': 'block'},
            name='ebpub-block-recent'),
        url(r'^streets/(\w{0})([-a-z0-9]{1,64})/%s/upcoming/$' % BLOCK_URL_REGEX,
            views.place_detail_timeline, {'place_type': 'block', 'show_upcoming': True},
            name='ebpub-block-upcoming'),
        url(r'^streets/(\w{0})([-a-z0-9]{1,64})/%s/overview/$' % BLOCK_URL_REGEX,
            views.place_detail_overview, {'place_type': 'block'},
            name='ebpub-block-overview'),
        url(r'^streets/(\w{0})([-a-z0-9]{1,64})/%s/feeds/$' % BLOCK_URL_REGEX,
            views.feed_signup, {'place_type': 'block'},
            name='ebpub-block-feed-signup'),
        url(r'^streets/(\w{0})([-a-z0-9]{1,64})/%s/alerts/$' % BLOCK_URL_REGEX,
            alert_views.signup, {'place_type': 'block'},
            name='ebpub-block-alerts-signup'),
        url(r'^rss/streets/(\w{0})([-a-z0-9]{1,64})/%s/$' % BLOCK_URL_REGEX,
            feeds.BlockFeed(), name='ebpub-block-rss'),
        )


urlpatterns += patterns(
    '',
    url(r'^([-\w]{4,32})/$', views.schema_detail, name='ebpub-schema-detail'),
    (r'^([-\w]{4,32})/search/$', views.search),
    (r'^([-\w]{4,32})/petition/$', petition_views.form_view, {'is_schema': True}),
    (r'^([-\w]{4,32})/petition/thanks/$', petition_views.form_thanks, {'is_schema': True}),
    url(r'^([-\w]{4,32})/detail/(\d{1,8})/$', views.newsitem_detail, name='ebpub-newsitem-detail'),
    url(r'^([-\w]{4,32})/filter_json/([^/].*)?/?$', views.schema_filter_geojson,
        name='ebpub-schema-filter-geojson'),
    url(r'^([-\w]{4,32})/(?:filter/)?([^/].*)?/$', views.schema_filter,
        name='ebpub-schema-filter'),

)

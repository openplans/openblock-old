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
from django.conf.urls.defaults import *
from ebpub.alerts import views as alert_views
from ebpub.db import feeds, views
from ebpub.db.constants import BLOCK_URL_REGEX
from ebpub.petitions import views as petition_views
from ebpub.utils.urlresolvers import metro_patterns


if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^(?P<path>(?:%s).*)$' % settings.DJANGO_STATIC_NAME_PREFIX.strip('/'),
         'django.views.static.serve', {'document_root': settings.EB_MEDIA_ROOT}),
    )
    urlpatterns += patterns('',
        (r'^(?P<path>(?:images|scripts|styles|openlayers).*)$', 'django.views.static.serve', {'document_root': settings.EB_MEDIA_ROOT}),
    )
else:
    urlpatterns = patterns('')

urlpatterns += patterns('',
    url(r'^$', views.homepage, name="ebpub-homepage"),
    (r'^search/$', views.search),
    (r'^news/$', views.schema_list),
    url(r'^locations/$', 'django.views.generic.simple.redirect_to', {'url': '/locations/neighborhoods/'}),
    url(r'^locations/([-_a-z0-9]{1,32})/$', views.location_type_detail, name='ebpub-loc-type-detail'),
    url(r'^locations/([-_a-z0-9]{1,32})/([-_a-z0-9]{1,32})/$', views.place_detail_timeline, {'place_type': 'location'}, name="ebpub-place-timeline"),
    url(r'^locations/([-_a-z0-9]{1,32})/([-_a-z0-9]{1,32})/overview/$', views.place_detail_overview, {'place_type': 'location'}, name="ebpub-place-overview"),
    (r'^locations/([-_a-z0-9]{1,32})/([-_a-z0-9]{1,32})/feeds/$', views.feed_signup, {'place_type': 'location'}),
    (r'^locations/([-_a-z0-9]{1,32})/([-_a-z0-9]{1,32})/alerts/$', alert_views.signup, {'place_type': 'location'}),
    (r'^locations/([-a-z0-9]{1,32})/([-a-z0-9]{1,32})/place.kml$', views.place_kml, {'place_type': 'location'}),
    (r'^rss/(.+)/$', feeds.feed_view),
    (r'^accounts/', include('ebpub.accounts.urls')),
    (r'^alerts/unsubscribe/(\d{1,10})/$', alert_views.unsubscribe),
    (r'^petitions/([-\w]{4,32})/$', petition_views.form_view, {'is_schema': False}),
    (r'^petitions/([-\w]{4,32})/thanks/$', petition_views.form_thanks, {'is_schema': False}),
    url(r'^api/place-lookup-chart/$', views.ajax_place_lookup_chart, name='ajax-place-lookup-chart'),
    url(r'^api/place-date-chart/$', views.ajax_place_date_chart, name='ajax-place-date-chart'),
    (r'^api/map-browser/location-types/(\d{1,9})/$', views.ajax_location_list),
    (r'^api/map-browser/locations/(\d{1,9})/$', views.ajax_location),
    (r'^api/newsitems.geojson/$', views.newsitems_geojson),
    (r'^api/dev1/', include('ebpub.openblockapi.urls')),
    (r'^widgets/', include('ebpub.widgets.urls'))
)

urlpatterns += metro_patterns(
    multi=(
        (r'^streets/$', views.city_list),
        (r'^streets/([-a-z]{3,40})/$', views.street_list),
        (r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/$', views.block_list),
        (r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/%s/$' % BLOCK_URL_REGEX, views.place_detail_timeline, {'place_type': 'block'}, 'ebpub-place-timeline'),
        (r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/%s/overview/$' % BLOCK_URL_REGEX, views.place_detail_overview, {'place_type': 'block'}, 'ebpub-place-overview'),
        (r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/%s/feeds/$' % BLOCK_URL_REGEX, views.feed_signup, {'place_type': 'block'}),
        (r'^streets/([-a-z]{3,40})/([-a-z0-9]{1,64})/%s/alerts/$' % BLOCK_URL_REGEX, alert_views.signup, {'place_type': 'block'}),
    ),
    single=(
        (r'^streets/()$', views.street_list),
        (r'^streets/()([-a-z0-9]{1,64})/$', views.block_list),
        (r'^streets/()([-a-z0-9]{1,64})/%s/$' % BLOCK_URL_REGEX, views.place_detail_timeline, {'place_type': 'block'}, 'ebpub-place-timeline'),
        (r'^streets/()([-a-z0-9]{1,64})/%s/overview/$' % BLOCK_URL_REGEX, views.place_detail_overview, {'place_type': 'block'}, 'ebpub-place-overview'),
        (r'^streets/()([-a-z0-9]{1,64})/%s/feeds/$' % BLOCK_URL_REGEX, views.feed_signup, {'place_type': 'block'}),
        (r'^streets/()([-a-z0-9]{1,64})/%s/alerts/$' % BLOCK_URL_REGEX, alert_views.signup, {'place_type': 'block'}),
    )
)

urlpatterns += patterns(
    '',
    url(r'^([-\w]{4,32})/$', views.schema_detail, name='ebpub-schema-detail'),
    url(r'^([-\w]{4,32})/about/$', views.schema_about, name='ebpub-schema-about'),
    (r'^([-\w]{4,32})/search/$', views.search),
    (r'^([-\w]{4,32})/petition/$', petition_views.form_view, {'is_schema': True}),
    (r'^([-\w]{4,32})/petition/thanks/$', petition_views.form_thanks, {'is_schema': True}),
    (r'^([-\w]{4,32})/by-date/(\d{4})/(\d\d?)/(\d\d?)/(\d{1,8})/$', views.newsitem_detail),
    url(r'^([-\w]{4,32})/(?:filter/)?([^/].+/)?$', views.schema_filter, name='schema-filter'),
)

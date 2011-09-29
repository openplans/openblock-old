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

"""
Unit tests for db.views.
"""

from django.core import urlresolvers
from django.utils import simplejson
from ebpub.db import models
from ebpub.db.urlresolvers import filter_reverse
from ebpub.db.views import BadAddressException
from ebpub.utils.django_testcase_backports import TestCase
import datetime
import logging
import mock
import urllib


class BaseTestCase(TestCase):

    _logger_keys = ('django.request',)

    def setUp(self):
        # Don't log 404 warnings, we expect a lot of them during these
        # tests.
        self._previous_levels = {}
        for key in self._logger_keys:
            logger = logging.getLogger(key)
            self._previous_levels[key] = logger.getEffectiveLevel()
            logger.setLevel(logging.ERROR)

    def tearDown(self):
        # Restore old log level.
        for key in self._logger_keys:
            logger = logging.getLogger(key)
            logger.setLevel(self._previous_levels[key])

class ViewTestCase(BaseTestCase):
    "Unit tests for views.py."
    fixtures = ('crimes',)

    def test_search__bad_schema(self):
        url = urlresolvers.reverse('ebpub.db.views.search', args=['kaboom'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_search__no_query(self):
        url = urlresolvers.reverse('ebpub.db.views.search', args=['crime'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], 'http://testserver/crime/')
        response = self.client.get(url + '?type=alert')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], 'http://testserver/crime/')

    def test_search(self):
        url = urlresolvers.reverse('ebpub.db.views.search', args=['crime'])
        response = self.client.get(url + '?q=228 S. Wabash Ave.')
        self.assertEqual(response.status_code, 200)
        assert 'location not found' in response.content.lower()
        # TODO: load a fixture with some locations and some news?

    @mock.patch('ebpub.db.views.NewsItem.location_url')
    def test_newsitem_detail(self, mock_location_url):
        mock_location_url.return_value = 'http://X'
        url = urlresolvers.reverse('ebpub.db.views.newsitem_detail',
                                   args=['crime', 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'crime title 1')
        self.assertContains(response, 'http://X')

    def test_locationtype_list_redirect(self):
        with self.settings(DEFAULT_LOCTYPE_SLUG='thingies'):
            response = self.client.get('/locations/')
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response['Location'], 'http://testserver/locations/thingies/')

    def test_schema_detail(self):
        response = self.client.get('/crime/')
        self.assertEqual(response.status_code, 200)
        # TODO: more than a smoke test!

    def test_schema_detail__notfound(self):
        response = self.client.get('/nonexistent/')
        self.assertEqual(response.status_code, 404)



class LocationDetailTestCase(BaseTestCase):
    fixtures = ('test-locationdetail-views.json',)

    def test_location_type_detail(self):
        url = urlresolvers.reverse('ebpub-loc-type-detail', args=['neighborhoods'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # TODO: more than a smoke test!

    @mock.patch('ebpub.db.views.today')
    def test_location_timeline(self, mock_today):
        mock_today.return_value = datetime.date(2006, 9, 26)
        url = urlresolvers.reverse('ebpub-location-recent',
                                   args=['neighborhoods', 'hood-1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['newsitem_list']), 1)
        self.assertEqual(response.context['newsitem_list'][0].title, 'crime title 1')

    def test_location_overview(self):
        url = urlresolvers.reverse('ebpub-location-overview',
                                   args=['neighborhoods', 'hood-1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # TODO: more than a smoke test!

    def test_feed_signup(self):
        url = urlresolvers.reverse('ebpub-feed-signup',
                                   args=['neighborhoods', 'hood-1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestAjaxViews(BaseTestCase):
    fixtures = ('crimes.json',)

    @mock.patch('ebpub.db.views.FilterChain')
    def test_ajax_place_lookup_chart__location(self, mock_chain):
        # Hack so isinstance(mock_chain(), FilterChain) works
        from ebpub.db import schemafilters
        mock_chain.return_value = mock.Mock(spec=schemafilters.FilterChain)
        mock_chain().return_value = mock_chain()
        mock_chain().make_url.return_value = 'foo'
        mock_chain().schema.url.return_value = 'bar'
        mock_chain().apply.return_value = models.NewsItem.objects.all()
        url = urlresolvers.reverse('ajax-place-lookup-chart')
        url += '?sf=13&pid=b:1000.8'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 3)

    def test_ajax_place_lookup_chart__bad_args(self):
        url = urlresolvers.reverse('ajax-place-lookup-chart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        response = self.client.get(url + '?sf=13')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(url + '?pid=b:1000.8')
        self.assertEqual(response.status_code, 404)


    @mock.patch('ebpub.db.views.today')
    @mock.patch('ebpub.db.views.FilterChain')
    def test_ajax_place_date_chart__location(self, mock_chain, mock_today):
        mock_today.return_value = datetime.date(2006, 11, 10)
        # Hack so isinstance(mock_chain(), FilterChain) works
        from ebpub.db import schemafilters
        mock_chain.return_value = mock.Mock(spec=schemafilters.FilterChain)
        mock_chain().return_value = mock_chain()
        mock_chain().make_url.return_value = 'foo'
        mock_chain().schema.url.return_value = 'bar'
        mock_chain().apply.return_value = models.NewsItem.objects.all()
        url = urlresolvers.reverse('ajax-place-date-chart') + '?s=1&pid=b:1000.8'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['date_chart']['total_count'], 2)
        self.assertEqual(len(response.context['date_chart']['dates']), 10)
        self.assertEqual(response.context['date_chart']['dates'][-1],
                         {'date': datetime.date(2006, 11, 8), 'count': 2})


    @mock.patch('ebpub.db.views.FilterChain')
    def test_newsitems_geojson__with_pid(self, mock_chain):
        mock_chain().apply.return_value = models.NewsItem.objects.all()
        url = urlresolvers.reverse('ajax-newsitems-geojson')
        url += '?schema=crime&pid=l:2000'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        items = simplejson.loads(response.content)
        self.assertEqual(items['type'], 'FeatureCollection')
        self.assertEqual(len(items['features']), 3)
        feat = items['features'][0]
        self.assertEqual(feat['type'], 'Feature')
        self.assertEqual(feat['properties']['title'], 'crime title 3')
        self.assertEqual(feat['geometry']['type'], 'Point')
        self.assert_('coordinates' in feat['geometry'])

    @mock.patch('ebpub.db.views.FilterChain')
    def test_newsitems_geojson__with_pid_no_schema(self, mock_chain):
        mock_chain().apply.return_value = models.NewsItem.objects.all()
        url = urlresolvers.reverse('ajax-newsitems-geojson')
        url += '?pid=b:1000.8'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        items = simplejson.loads(response.content)
        self.assertEqual(items['type'], 'FeatureCollection')
        self.assertEqual(len(items['features']), 3)


class TestSchemaFilterView(BaseTestCase):

    fixtures = ('test-schemafilter-views.json',)

    def test_filter_by_no_args(self):
        url = filter_reverse('crime', [])
        response = self.client.get(url)
        self.assertContains(response, 'choose a location')
        self.assertContains(response, 'id="date-filtergroup"')

    def test_filter_by_location_choices(self):
        url = filter_reverse('crime', [('locations', 'neighborhoods')])
        response = self.client.get(url)
        self.assertContains(response, 'Select Neighborhood')
        self.assertContains(response, 'Hood 1')
        self.assertContains(response, 'Hood 2')

    def test_filter_by_location_detail(self):
        url = filter_reverse('crime', [('locations', 'neighborhoods', 'hood-1')])
        response = self.client.get(url)
        self.assertContains(response, 'Hood 1')
        self.assertNotContains(response, 'Hood 2')
        self.assertContains(response, 'Remove this filter')

    @mock.patch('ebpub.db.schemafilters.logger')
    @mock.patch('ebpub.db.schemafilters.FilterChain.update_from_request')
    def test_filter_by_ambiguous_address(self, mock_from_request, mock_logger):
        # Using Mocks here causes eb_filter to call FilterChain.make_url
        # with additions that it doesn't understand. That's fine for this test,
        # but causes logging spew, hence we mock the logger too.
        url = filter_reverse('crime', [('by-foo', 'bar')]) + '?address=foofoo'
        mock_result = {'address': 'foofoo', 'block': mock.Mock()}
        mock_result['block'].url = '/foofoo/'
        mock_from_request.side_effect = BadAddressException('123 somewhere', 3, 
                                                            [mock_result, mock_result])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'db/filter_bad_address.html')

    @mock.patch('ebpub.db.schemafilters.FilterChain.update_from_request')
    @mock.patch('ebpub.db.schemafilters.FilterChain.make_url')
    def test_filter__normalized_redirect(self, mock_make_url, mock_from_request):
        from ebpub.db import schemafilters
        mock_make_url.return_value = '/whee/'
        mock_from_request.return_value = schemafilters.FilterChain()
        url = filter_reverse('crime', [('by-foo', 'bar')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], 'http://testserver/whee/')

    def test_filter__charting_disallowed_redirect(self):
        # could make a different fixture, but, meh.
        crime = models.Schema.objects.get(slug='crime')
        crime.allow_charting = False
        crime.save()
        url = filter_reverse('crime', [('by-foo', 'bar')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['location'], 'http://testserver/crime/')

    @mock.patch('ebpub.db.schemafilters.FilterChain.update_from_query_params')
    def test_filter__bad_date(self, mock_update):
        from ebpub.db.views import BadDateException
        mock_update.side_effect = BadDateException("oh no")
        url = filter_reverse('crime', [('by-date', '2006-11-01', '2006-11-30')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter__bad_params(self):
        url = filter_reverse('crime', [('by-foo', 'bar')])
        url = url.replace(urllib.quote('='), 'X')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_daterange(self):
        url = filter_reverse('crime', [('by-date', '2006-11-01', '2006-11-30')])
        response = self.client.get(url)
        self.assertContains(response, 'Clear')
        self.assertNotContains(response, "crime title 1")
        self.assertContains(response, "crime title 2")
        self.assertContains(response, "crime title 3")

    def test_filter_by_pubdate_daterange(self):
        url = filter_reverse('crime', [('by-pub-date', '2006-11-01', '2006-11-30')])
        response = self.client.get(url)
        self.assertContains(response, 'Clear')
        self.assertNotContains(response, "crime title 1")
        self.assertContains(response, "crime title 2")
        self.assertContains(response, "crime title 3")

    def test_filter__only_one_date_allowed(self):
        url = filter_reverse('crime',
                             [('by-date', '2006-11-01', '2006-11-30'),
                              ('by-pub-date', '2006-11-01', '2006-11-30')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_filter__invalid_daterange(self):
        url = filter_reverse('crime', [('by-date', '')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        url = filter_reverse('crime', [('by-date', 'whoops', 'ouchie')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        url = filter_reverse('crime', [('by-date', '2006-11-30', 'ouchie')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_filter_by_day(self):
        url = filter_reverse('crime', [('by-date', '2006-09-26', '2006-09-26')])
        response = self.client.get(url)
        self.assertContains(response, "crime title 1")
        self.assertNotContains(response, "crime title 2")
        self.assertNotContains(response, "crime title 3")


    def test_filter_by_attributes__text(self):
        url = filter_reverse('crime', [('by-status', 'status 9-19')])
        response = self.client.get(url)
        self.assertEqual(len(response.context['newsitem_list']), 1)
        self.assertContains(response, "crime title 1")
        self.assertNotContains(response, "crime title 2")
        self.assertNotContains(response, "crime title 3")


    def test_filter_by_attributes__text__empty(self):
        url = filter_reverse('crime', [('by-status', '')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_attributes__bad_attr(self):
        url = filter_reverse('crime', [('by-bogosity', 'anything')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_attributes__bad_value(self):
        url = filter_reverse('crime', [('by-status', 'bogus')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "crime title ")

    def test_filter_by_street__missing_street(self):
        url = filter_reverse('crime', [('streets', '')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_street__missing_block(self):
        url = filter_reverse('crime', [('streets', 'wabash-ave',)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_street__bad_block(self):
        url = filter_reverse('crime', [('streets', 'bogus',)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        url = filter_reverse('crime', [('streets', 'bogus street', 'bogus block', '8-blocks')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @mock.patch('ebpub.streets.models.proper_city')
    def test_filter_by_block__no_radius(self, mock_proper_city):
        # We just fall back to the default radius.
        mock_proper_city.return_value = 'chicago'
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        fixed_url = filter_reverse('crime', [
                ('streets', 'wabash-ave', '216-299n-s', '8-blocks')])
        self.assert_(response['location'].endswith(urllib.unquote(fixed_url)))

    @mock.patch('ebpub.streets.models.proper_city')
    def test_filter_by_block(self, mock_proper_city):
        mock_proper_city.return_value = 'chicago'
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s', '8-blocks')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # TODO: more assertions

    @mock.patch('ebpub.streets.models.proper_city')
    def test_filter__only_one_location_allowed(self, mock_proper_city):
        mock_proper_city.return_value = 'chicago'
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s', '8-blocks'),
                                       ('locations', 'neighborhoods', 'hood-1'),
                                       ])
        response = self.client.get(url)
        url = filter_reverse('crime', [('locations', 'neighborhoods', 'hood-1'),
                                       ('streets', 'wabash-ave', '216-299n-s', '8')
                                       ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter__by_location__not_found(self):
        url = filter_reverse('crime', [('locations', 'anything')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter__by_location__empty_location(self):
        url = filter_reverse('crime', [('locations', '')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_location(self):
        url = filter_reverse('crime', [('locations', 'neighborhoods', 'hood-1'),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hood 1')

    def test_filter__by_bad_lookup_attr(self):
        url = filter_reverse('crime', [('by-fleezleglop', '214', ),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter__by_lookup_attr(self):
        url = filter_reverse('crime', [('by-beat', 'beat-214', ),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Police Beat 214')

    def test_filter__by_lookup__not_specified(self):
        url = filter_reverse('crime', [('by-beat', ''),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'db/filter_lookup_list.html')

    def test_filter__by_m2m_lookup_attr(self):
        # XXX todo.
        # I don't think there are any m2m lookups in crimes.json yet
        pass

    def test_filter__by_boolean_attr__true(self):
        url = filter_reverse('crime', [('by-arrests', 'yes',),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'crime title 2')
        self.assertNotContains(response, 'crime title 1')
        self.assertNotContains(response, 'crime title 3')

    def test_filter__by_boolean_attr__false(self):
        url = filter_reverse('crime', [('by-arrests', 'no',),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'crime title 2')
        self.assertContains(response, 'crime title 1')
        self.assertContains(response, 'crime title 3')

    def test_filter__by_boolean__invalid(self):
        url = filter_reverse('crime', [('by-arrests', 'yes', 'no'),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        url = filter_reverse('crime', [('by-arrests', 'maybe'),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter__invalid_argname(self):
        url = filter_reverse('crime', [('bogus-key', 'bogus-value')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    @mock.patch('ebpub.db.schemafilters.logger')
    @mock.patch('ebpub.db.models.AggregateFieldLookup.objects.filter')
    def test_filter__has_more(self, mock_aggr, mock_logger):
        # Using Mocks here causes eb_filter to call FilterChain.make_url
        # with additions that it doesn't understand. That's fine for this test,
        # but causes logging spew, hence we mock the logger too.
        mock_item = mock.Mock()
        mock_item.return_value = mock_item
        mock_item.alters_data = False
        mock_aggr().select_related().order_by.return_value = [mock_item] * 100
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        lookup_list = response.context['lookup_list']
        self.assert_(lookup_list)
        for lookup_info in lookup_list:
            self.assertEqual(lookup_info['has_more'], True)

    def test_filter__pagination__invalid_page(self):
        url = filter_reverse('crime', [('by-status', 'status 9-19')])
        url += '?page=oops'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter__pagination__empty_page(self):
        url = filter_reverse('crime', [('by-status', 'status 9-19')])
        url += '?page=99'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @mock.patch('ebpub.db.views.FilterChain', spec=True)
    def test_filter__pagination__has_more(self, mock_chain):
        url = filter_reverse('crime', [('by-status', 'status 9-19')])
        url += '?page=2'
        # We can mock the FilterChain to get a very long list of NewsItems
        # without actually creating them in the db, but it means
        # also mocking a ton of methods used by schema_filter or filter.html.
        # (We can't just patch text_search() anymore because now there's more
        # filtering after that.)
        # TODO: this is pretty brittle. Worth it?
        mock_qs = mock.Mock()
        mock_qs.filter.return_value = mock_qs
        newsitem = models.NewsItem.objects.all()[0]
        mock_qs.order_by.return_value = [newsitem] * 100

        mock_chain.return_value = mock_chain
        mock_chain.apply.return_value = mock_qs
        mock_chain.__contains__ = lambda self, other: False
        mock_chain.get.return_value = None
        mock_chain.validate.return_value = {}
        mock_chain.make_breadcrumbs.return_value = []
        mock_chain.values = []
        mock_chain.lookup_descriptions = []
        mock_chain.make_url.return_value = urllib.unquote(url)  # Avoid redirect.

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['has_next'], True)
        self.assertEqual(response.context['has_previous'], True)

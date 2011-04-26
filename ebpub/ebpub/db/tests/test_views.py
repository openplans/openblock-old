#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
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
from django.test import TestCase
from django.utils import simplejson

from ebpub.db.urlresolvers import filter_reverse
from ebpub.db.views import _schema_filter_normalize_url
from ebpub.db.views import BadAddressException

from ebpub.db import models

# Once we are on django 1.3, this becomes "from django.test.client import RequestFactory"
from client import RequestFactory
import mock
import urllib


class ViewTestCase(TestCase):
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

    def test_location_redirect(self):
        # redirect to neighborhoods by default
        response = self.client.get('/locations/')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'http://testserver/locations/neighborhoods/')

    def test_schema_detail(self):
        response = self.client.get('/crime/')
        self.assertEqual(response.status_code, 200)
        # TODO: more than a smoke test!

    def test_schema_detail__notfound(self):
        response = self.client.get('/nonexistent/')
        self.assertEqual(response.status_code, 404)



class LocationDetailTestCase(TestCase):
    fixtures = ('crimes', 'test-locationtypes.json', 'test-locations.json')

    def test_location_type_detail(self):
        url = urlresolvers.reverse('ebpub-loc-type-detail', args=['neighborhoods'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # TODO: more than a smoke test!

    def test_location_timeline(self):
        url = urlresolvers.reverse('ebpub-place-timeline',
                                   args=['neighborhoods', 'hood-1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # TODO: more than a smoke test!

    def test_location_overview(self):
        url = urlresolvers.reverse('ebpub-place-overview',
                                   args=['neighborhoods', 'hood-1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # TODO: more than a smoke test!

    def test_feed_signup(self):
        url = urlresolvers.reverse('ebpub-feed-signup',
                                   args=['neighborhoods', 'hood-1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestAjaxViews(TestCase):
    fixtures = ('crimes.json',)

    @mock.patch('ebpub.db.views.FilterChain')
    def test_ajax_place_lookup_chart__location(self, mock_chain):
        # Hack so isinstance(mock_chain(), FilterChain) works
        from ebpub.db import schemafilters
        mock_chain.return_value = mock.Mock(spec=schemafilters.FilterChain)
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


    @mock.patch('ebpub.db.views.FilterChain')
    def test_ajax_place_newsitems(self, mock_chain):
        mock_chain().apply.return_value = models.NewsItem.objects.all()
        url = urlresolvers.reverse('ajax-place-newsitems')
        url += '?s=1&pid=l:2000'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        items = simplejson.loads(response.content)
        self.assert_('bunches' in items.keys())
        self.assert_('ids' in items.keys())
        self.assertEqual(sorted(items['ids']), [1, 2, 3])

    @mock.patch('ebpub.db.views.FilterChain')
    def test_ajax_place_date_chart__location(self, mock_chain):
        # Hack so isinstance(mock_chain(), FilterChain) works
        from ebpub.db import schemafilters
        mock_chain.return_value = mock.Mock(spec=schemafilters.FilterChain)
        mock_chain().make_url.return_value = 'foo'
        mock_chain().schema.url.return_value = 'bar'
        mock_chain().apply.return_value = models.NewsItem.objects.all()
        url = urlresolvers.reverse('ajax-place-date-chart') + '?s=1&pid=b:1000.8'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['date_chart']['total_count'], 1)
        self.assertEqual(len(response.context['date_chart']['dates']), 8)
        import datetime
        self.assertEqual(response.context['date_chart']['dates'][-1],
                         {'date': datetime.date(2006, 11, 8), 'count': 1})


    @mock.patch('ebpub.db.views.FilterChain')
    def test_newsitems_geojson__with_pid(self, mock_chain):
        mock_chain().apply.return_value = models.NewsItem.objects.all()
        url = urlresolvers.reverse('newsitems-geojson')
        url += '?schema=crime&pid=l:2000'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        items = simplejson.loads(response.content)
        self.assertEqual(items['type'], 'FeatureCollection')
        self.assertEqual(len(items['features']), 3)
        feat = items['features'][0]
        self.assertEqual(feat['type'], 'Feature')
        self.assertEqual(feat['properties']['title'], 'crime title 2')
        self.assert_('popup_html' in feat['properties'])
        self.assertEqual(feat['geometry']['type'], 'Point')
        self.assert_('coordinates' in feat['geometry'])

    @mock.patch('ebpub.db.views.FilterChain')
    def test_newsitems_geojson__with_pid_no_schema(self, mock_chain):
        mock_chain().apply.return_value = models.NewsItem.objects.all()
        url = urlresolvers.reverse('newsitems-geojson')
        url += '?pid=b:1000.8'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        items = simplejson.loads(response.content)
        self.assertEqual(items['type'], 'FeatureCollection')
        self.assertEqual(len(items['features']), 3)


class TestSchemaFilterView(TestCase):

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

    @mock.patch('ebpub.db.views._schema_filter_normalize_url')
    def test_filter_by_bad_address(self, mock_normalize):
        mock_normalize.side_effect = BadAddressException('123 somewhere', 3, ['foo', 'bar'])
        url = filter_reverse('crime', [('by-foo', 'bar')]) + '?address=foofoo'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'db/filter_bad_address.html')

    @mock.patch('ebpub.db.views._schema_filter_normalize_url')
    def test_filter__normalized_redirect(self, mock_normalize):
        mock_normalize.return_value = 'http://example.com/whee'
        url = filter_reverse('crime', [('by-foo', 'bar')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], 'http://example.com/whee')

    def test_filter__charting_disallowed_redirect(self):
        # could make a different fixture, but, meh.
        crime = models.Schema.objects.get(slug='crime')
        crime.allow_charting = False
        crime.save()
        url = filter_reverse('crime', [('by-foo', 'bar')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['location'], 'http://testserver/crime/')

    @mock.patch('ebpub.db.views._schema_filter_normalize_url')
    def test_filter_bad_date(self, mock_normalize):
        from ebpub.db.views import BadDateException
        mock_normalize.side_effect = BadDateException("oh no")
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

    def test_filter__only_one_location_allowed(self):
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s', '8-blocks'),
                                       ('locations', 'neighborhoods', 'hood-1'),
                                       ])
        response = self.client.get(url)
        url = filter_reverse('crime', [('locations', 'neighborhoods', 'hood-1'),
                                       ('streets', 'wabash-ave', '216-299n-s', '8')
                                       ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter__by_location__unknown(self):
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

    def test_filter__by_boolean__unspecified(self):
        url = filter_reverse('crime', [('by-arrests', '')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template[0].name, 'db/filter_lookup_list.html')

    def test_filter__invalid_argname(self):
        url = filter_reverse('crime', [('bogus-key', 'bogus-value')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @mock.patch('ebpub.db.models.AggregateFieldLookup.objects.filter')
    def test_filter__has_more(self, mock_aggr):
        mock_aggr().select_related().order_by.return_value = [mock.Mock()] * 100
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

    @mock.patch('ebpub.db.views.cluster_newsitems')
    @mock.patch('ebpub.db.views.FilterChain')
    def test_filter__pagination__has_more(self, mock_chain, mock_cluster):
        url = filter_reverse('crime', [('by-status', 'status 9-19')])
        url += '?page=2'
        mock_cluster.return_value = {}
        # We can mock the FilterChain to get a very long list of NewsItems
        # without actually creating them in the db, but it means
        # also mocking a ton of methods used by schema_filter or filter.html.
        # (We can't just patch text_search() anymore because now there's more
        # filtering after that.)
        # TODO: this is pretty brittle.
        mock_chain.from_request.return_value = mock_chain
        mock_chain.normalized_clone.return_value = mock_chain
        mock_chain.apply.return_value = mock_chain
        mock_chain.order_by.return_value = mock_chain
        mock_chain.__contains__ = lambda self, other: False
        mock_chain.validate.return_value = {}
        mock_chain.make_breadcrumbs.return_value = []
        mock_chain.values = []
        mock_chain.lookup_descriptions = []
        newsitem = models.NewsItem.objects.all()[0]
        # Finally, here's our list of stuff.
        mock_chain.filter.return_value = [newsitem] * 100

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['has_next'], True)
        self.assertEqual(response.context['has_previous'], True)


class TestNormalizeSchemaFilterView(TestCase):

    fixtures = ('test-schemafilter-views.json',)

    def test_normalize_filter_url__ok(self):
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n', '8'),])
        request = RequestFactory().get(url)
        self.assertEqual(None, _schema_filter_normalize_url(request))

    @mock.patch('ebpub.db.views.SmartGeocoder.geocode')
    def test_normalize_filter_url__intersection(self, mock_geocode):
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter']) + '?address=foo+and+bar'
        from ebpub.streets.models import Block, Intersection, BlockIntersection
        intersection = mock.Mock(spec=Intersection)
        blockintersection = mock.Mock(spec=BlockIntersection)
        blockintersection.block = Block.objects.get(street_slug='wabash-ave', from_num=216)
        intersection.blockintersection_set.all.return_value = [blockintersection]
        mock_geocode.return_value = {'intersection': intersection,
                                     'block': None}
        request = RequestFactory().get(url)
        result = _schema_filter_normalize_url(request)
        expected = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s', '8'),])

        self.assertEqual(result, expected)

    @mock.patch('ebpub.db.views.SmartGeocoder.geocode')
    def test_normalize_filter_url__bad_intersection(self, mock_geocode):
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter']) + '?address=foo+and+bar'
        from ebpub.streets.models import Block, Intersection, BlockIntersection
        intersection = mock.Mock(spec=Intersection)
        blockintersection = mock.Mock(spec=BlockIntersection)
        blockintersection.block = Block.objects.get(street_slug='wabash-ave', from_num=216)
        mock_geocode.return_value = {'intersection': intersection,
                                     'block': None}
        # Empty intersection list.
        intersection.blockintersection_set.all.return_value = []
        request = RequestFactory().get(url)
        self.assertRaises(IndexError, _schema_filter_normalize_url, request)
        # Or, no block or intersection at all.
        mock_geocode.return_value = {'intersection': None, 'block': None}
        self.assertRaises(NotImplementedError, _schema_filter_normalize_url, request)


    def test_normalize_filter_url__bad_address(self):
        from ebpub.db.views import _schema_filter_normalize_url
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter'])
        url += '?address=123+nowhere+at+all&radius=8'

        request = RequestFactory().get(url)
        self.assertRaises(BadAddressException,
                          _schema_filter_normalize_url, request)


    @mock.patch('ebpub.db.views.SmartGeocoder.geocode')
    def test_normalize_filter_url__ambiguous_address(self, mock_geocode):
        from ebpub.geocoder import AmbiguousResult
        mock_geocode.side_effect = AmbiguousResult(['foo', 'bar'])
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter'])
        url += '?address=anything' # doesn't matter because of mock_geocode
        request = RequestFactory().get(url)
        self.assertRaises(BadAddressException, _schema_filter_normalize_url, request)

    @mock.patch('ebpub.db.views.SmartGeocoder.geocode')
    def test_normalize_filter_url__address_query(self, mock_geocode):
        from ebpub.streets.models import Block
        block = Block.objects.get(street_slug='wabash-ave', from_num=216)
        mock_geocode.return_value = {
            'city': block.left_city.title(),
            'zip': block.left_zip,
            'point': block.geom.centroid,
            'state': block.left_state,
            'intersection_id': None,
            'address': u'216 N Wabash Ave',
            'intersection': None,
            'block': block,
            }
        from ebpub.db.views import _schema_filter_normalize_url
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter'])
        url += '?address=216+n+wabash+st&radius=8'

        expected_url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s', '8'),])
        request = RequestFactory().get(url)
        normalized_url = _schema_filter_normalize_url(request)
        self.assertEqual(expected_url, normalized_url)

    def test_normalize_filter_url__bad_dates(self):
        from ebpub.db.views import BadDateException
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter'])
        request = RequestFactory().get(url + '?start_date=12/31/1899&end_date=01/01/2011')
        self.assertRaises(BadDateException, _schema_filter_normalize_url, request)

        request = RequestFactory().get(url + '?start_date=01/01/2011&end_date=12/31/1899')
        self.assertRaises(BadDateException, _schema_filter_normalize_url, request)

        request = RequestFactory().get(url + '?start_date=Whoops&end_date=Bzorch')
        self.assertRaises(BadDateException, _schema_filter_normalize_url, request)


    def test_normalize_filter_url__date_query(self):
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter'])
        url += '?start_date=12/01/2010&end_date=01/01/2011'
        request = RequestFactory().get(url)
        result = _schema_filter_normalize_url(request)
        expected = filter_reverse('crime', [('by-date', '2010-12-01', '2011-01-01')])
        self.assertEqual(result, expected)


    def test_normalize_filter_url__textsearch_query(self):
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter'])
        url += '?textsearch=foo&q=hello+goodbye'
        request = RequestFactory().get(url)
        result = _schema_filter_normalize_url(request)
        expected = filter_reverse('crime', [('by-foo', 'hello goodbye')])
        self.assertEqual(result, expected)

    def test_normalize_filter_url__both_args_and_query(self):
        url = filter_reverse('crime', [('by-date', '2011-04-05', '2011-04-06')])
        url += '?textsearch=foo&q=bar'
        request = RequestFactory().get(url)
        result = _schema_filter_normalize_url(request)
        expected = filter_reverse('crime', [('by-date', '2011-04-05', '2011-04-06'),
                                            ('by-foo', 'bar')])
        self.assertEqual(result, expected)


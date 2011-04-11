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
from django.test import TestCase

from ebpub.db.views import _schema_filter_normalize_url
from ebpub.db.views import BadAddressException

# Once we are on django 1.3, this becomes "from django.test.client import RequestFactory"
from client import RequestFactory
from client import mock_with_attributes
import mock
import urllib
import posixpath


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


    def test_newsitem_detail(self):
        # response = self.client.get('')
        pass

    def test_location_redirect(self):
        # redirect to neighborhoods by default
        response = self.client.get('/locations/')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'http://testserver/locations/neighborhoods/')

    def test_location_type_detail(self):
        # response = self.client.get('')
        pass

    def test_location_detail(self):
        # response = self.client.get('')
        pass

    def test_schema_detail(self):
        response = self.client.get('/crime/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/nonexistent/')
        self.assertEqual(response.status_code, 404)

    def test_schema_xy_detail(self):
        # response = self.client.get('')
        pass

def filter_reverse(slug, args):
    # Generate a reverse schema_filter URL.
    # XXX This should probably turn into something real,
    # not just a test helper.
    for i, a  in enumerate(args):
        if isinstance(a, tuple) or isinstance(a, list):
            # The first item is the arg name, the rest are arg values.
            if len(a) > 1:
                name = a[0]
                values = ','.join(a[1:])
                args[i] = '%s=%s' % (name, values)
            else:
                # This is allowed eg. for showing a list of available
                # Blocks, or Lookup values, etc.
                args[i] = a[0]
        else:
            assert isinstance(a, basestring)
    argstring = urllib.quote(';'.join(args)) #['%s=%s' % (k, v) for (k, v) in args])
    if not argstring:
        argstring = 'filter'
    url = urlresolvers.reverse('ebpub-schema-filter', args=[slug])
    url = '%s/%s/' % (url, argstring)
    # Normalize duplicate slashes, dots, and the like.
    url = posixpath.normpath(url) + '/'
    return url

class TestLocationFilter(TestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json',
                )

    def _make_filter(self, typeslug=None, loc=None):
        from ebpub.db import models
        crime = mock.Mock(spec=models.Schema)
        from ebpub.db.schemafilters import LocationFilter
        reverse_args = ['locations']
        if typeslug is not None:
            reverse_args.append(typeslug)
            if loc is not None:
                reverse_args.append(loc)
        url = filter_reverse('crime', [reverse_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        filt = LocationFilter(req, context, None, *reverse_args[1:])
        return filt

    def test_filter__errors(self):
        from ebpub.db.schemafilters import FilterError
        self.assertRaises(FilterError, self._make_filter)

    def test_filter_by_location_choices(self):
        filt = self._make_filter('zipcodes')
        more_needed = filt.more_info_needed()
        self.assertEqual(more_needed['lookup_type'], u'ZIP Code')
        self.assertEqual(more_needed['lookup_type_slug'], 'zipcodes')
        self.assert_(len(more_needed['lookup_list']) > 0)

    def test_filter_by_location_detail(self):
        filt = self._make_filter('zipcodes', 'zip-1')
        self.assertEqual(filt.more_info_needed(), {})
        # TODO: test apply()

class TestBlockFilter(TestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json',
                #'wabash.yaml',
                )

    def _make_filter(self, street_slug=None, block_range=None, block_radius=None):
        from ebpub.db import models
        crime = mock.Mock(spec=models.Schema)
        from ebpub.db.schemafilters import BlockFilter
        reverse_args = ['streets']
        if street_slug is not None:
            reverse_args.append(street_slug)
            if block_range is not None:
                reverse_args.append(block_range)
                if block_radius is not None:
                    reverse_args.append(block_radius)
        url = filter_reverse('crime', [reverse_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        filt = BlockFilter(req, context, None, *reverse_args[1:])
        return filt

    def test_filter__errors(self):
        from ebpub.db.schemafilters import FilterError
        self.assertRaises(FilterError, self._make_filter)
        self.assertRaises(FilterError, self._make_filter, '')
        self.assertRaises(FilterError, self._make_filter, 'wabash-ave')
        self.assertRaises(FilterError, self._make_filter, 'wabash-ave', '200-298s')
        try:
            # Re-testing that last one so we can inspect the exception.
            self._make_filter('wabash-ave', '200-298s')
        except FilterError, e:
            import urllib
            self.assertEqual(urllib.quote(e.url), filter_reverse('crime', [('streets', 'wabash-ave', '200-298s', '8-blocks')]))

    def test_filter__ok(self):
        filt = self._make_filter('wabash-ave', '200-298s', '8-blocks')
        self.assertEqual(filt.more_info_needed(), {})
        # TODO: test apply()


class TestDateFilter(TestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json',
                )

    def _make_filter(self, *url_args):
        crime = mock.Mock()
        from ebpub.db.schemafilters import DateFilter
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        filt = DateFilter(req, context, None, *url_args[1:])
        return filt

    def test_filter__errors(self):
        from ebpub.db.schemafilters import FilterError
        self.assertRaises(FilterError, self._make_filter, '')
        self.assertRaises(FilterError, self._make_filter, 'by-date')
        self.assertRaises(FilterError, self._make_filter, 'by-date', 'bogus')
        self.assertRaises(FilterError, self._make_filter, 'by-date', 'bogus', 'bogus')
        self.assertRaises(FilterError, self._make_filter, 'by-date', '2011-04-07')

    def test_filter__ok(self):
        filt = self._make_filter('by-date', '2011-04-07', '2011-04-08')
        self.assertEqual(filt.more_info_needed(), {})
        # TODO: test apply()


class TestBoolFilter(TestCase):

    fixtures = ('crimes.json',)

    def _make_filter(self, *url_args):
        crime = mock.Mock()
        from ebpub.db.schemafilters import BoolFilter
        from ebpub.db import models
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        sf_slug = url_args[0][3:]   # 'by-foo' -> 'foo'
        sf = models.SchemaField.objects.get(name=sf_slug)
        filt = BoolFilter(req, context, None, *url_args[1:], schemafield=sf)
        return filt

    def test_filter__errors(self):
        from ebpub.db.schemafilters import FilterError
        self.assertRaises(FilterError, self._make_filter, 'by-arrests', 'maybe')
        self.assertRaises(FilterError, self._make_filter, 'by-arrests', 'maybe', 'no')

    def test_filter__ok(self):
        filt = self._make_filter('by-arrests', 'no')
        self.assertEqual(filt.more_info_needed(), {})
        # TODO: test apply()

    def test_filter__more_needed(self):
        filt = self._make_filter('by-arrests')
        more_needed = filt.more_info_needed()
        self.assertEqual(more_needed['lookup_type_slug'], 'arrests')


class TestLookupFilter(TestCase):

    fixtures = ('crimes.json',)

    def _make_filter(self, *url_args):
        crime = mock.Mock()
        from ebpub.db.schemafilters import LookupFilter
        from ebpub.db import models
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        sf_slug = url_args[0][3:]   # 'by-foo' -> 'foo'
        sf = models.SchemaField.objects.get(name=sf_slug)
        filt = LookupFilter(req, context, None, *url_args[1:], schemafield=sf)
        return filt

    def test_filter__errors(self):
        from ebpub.db.schemafilters import FilterError
        #self.assertRaises(FilterError, self._make_filter, 'by-beat', )
        self.assertRaises(FilterError, self._make_filter, 'by-beat', 'whoops')

    def test_filter__more_needed(self):
        filt = self._make_filter('by-beat')
        more_needed = filt.more_info_needed()
        self.assert_(more_needed)
        self.assertEqual(more_needed['lookup_type'], 'Beat')
        self.assertEqual(more_needed['lookup_type_slug'], 'beat')
        self.assertEqual(len(more_needed['lookup_list']), 2)


    def test_filter__ok(self):
        filt = self._make_filter('by-beat', 'beat-214', )
        self.assertEqual(filt.more_info_needed(), {})
        # TODO: test apply()


class TestTextFilter(TestCase):

    fixtures = ('crimes.json',)

    def _make_filter(self, *url_args):
        crime = mock.Mock()
        from ebpub.db.schemafilters import TextSearchFilter
        from ebpub.db import models
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        sf_slug = url_args[0][3:]   # 'by-foo' -> 'foo'
        sf = models.SchemaField.objects.get(name=sf_slug)
        self.mock_qs = mock.Mock()
        filt = TextSearchFilter(req, context, self.mock_qs, *url_args[1:], schemafield=sf)
        return filt

    def test_filter__errors(self):
        from ebpub.db.schemafilters import FilterError
        self.assertRaises(FilterError, self._make_filter, 'by-status')

    def test_filter__ok(self):
        filt = self._make_filter('by-status', 'status 9-19')
        self.assertEqual(filt.more_info_needed(), {})
        filt.apply()
        self.assertEqual(self.mock_qs.text_search.call_count, 1)

class TestSchemaFilterView(TestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json', 'crimes.json',
                'wabash.yaml',
                )

    def test_filter_by_no_args(self):
        url = filter_reverse('crime', [])
        response = self.client.get(url)
        self.assertContains(response, 'choose a location')
        self.assertContains(response, 'id="date-filtergroup"')

    def test_filter_by_location_choices(self):
        url = filter_reverse('crime', [('locations', 'zipcodes')])
        response = self.client.get(url)
        self.assertContains(response, 'Select ZIP Code')
        self.assertContains(response, 'Zip 1')
        self.assertContains(response, 'Zip 2')

    def test_filter_by_location_detail(self):
        url = filter_reverse('crime', [('locations', 'zipcodes', 'zip-1')])
        response = self.client.get(url)
        self.assertContains(response, 'Zip 1')
        self.assertNotContains(response, 'Zip 2')
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
        from ebpub.db import models
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


    def test_filter_by_block__no_radius(self):
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        fixed_url = filter_reverse('crime', [
                ('streets', 'wabash-ave', '216-299n-s', '8-blocks')])
        self.assert_(response['location'].endswith(urllib.unquote(fixed_url)))

    def test_filter_by_block(self):
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s', '8-blocks')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @mock.patch('ebpub.db.schemafilters.get_metro')
    @mock.patch('ebpub.db.schemafilters.get_place_info_for_request')
    def test_filter_by_block__multicity(self, mock_get_place_info, mock_get_metro):
        def _mock_get_place_info(request, *args, **kwargs):
            block = mock_with_attributes(
                dict(from_num=99, to_num=100, street_slug='something',
                     pretty_name='99-100 somethign st'))
            return {'newsitem_qs': kwargs['newsitem_qs'],
                    'place': block,
                    'is_block': True,}

        mock_get_place_info.side_effect = _mock_get_place_info
        mock_get_metro.return_value = {'multiple_cities': True}
        url = filter_reverse('crime', [('streets', 'boston', 'wabash-ave', '216-299n-s', '8-blocks')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Boston')

    def test_filter__only_one_location_allowed(self):
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s', '8'),
                                       ('locations', 'zipcodes', 'zip-1'),
                                       ])
        response = self.client.get(url)
        url = filter_reverse('crime', [('locations', 'zipcodes', 'zip-1'),
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
        url = filter_reverse('crime', [('locations', 'zipcodes', 'zip-1'),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Zip 1')

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
    @mock.patch('ebpub.db.models.NewsItemQuerySet.text_search')
    def test_filter__pagination__has_more(self, mock_search, mock_cluster):
        url = filter_reverse('crime', [('by-status', 'status 9-19')])
        url += '?page=2'
        mock_search.return_value = [mock.Mock()] * 100
        mock_cluster.return_value = {}
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['has_next'], True)
        self.assertEqual(response.context['has_previous'], True)


class TestNormalizeSchemaFilterView(TestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json', 'wabash.yaml',
                )

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

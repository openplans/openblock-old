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



 # Once we are on django 1.3, this becomes "from django.test.client import RequestFactory"
from client import RequestFactory
from client import mock_with_attributes
from django.test import TestCase
from ebpub.db.schemafilters import FilterError
from ebpub.db.views import filter_reverse
from ebpub.db import models
import mock
import random


class TestSchemaFilter(TestCase):

    def test_get(self):
        from ebpub.db.schemafilters import SchemaFilter
        fil = SchemaFilter('dummy request', 'dummy context')
        self.assertEqual(fil.get('foo'), None)
        self.assertEqual(fil.get('foo', 'bar'), 'bar')

    def test_getitem(self):
        from ebpub.db.schemafilters import SchemaFilter
        fil = SchemaFilter('dummy request', 'dummy context')
        fil.foo = 'bar'
        self.assertEqual(fil['foo'], 'bar')
        self.assertRaises(KeyError, fil.__getitem__, 'bar')


class TestLocationFilter(TestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json',
                )

    def _make_filter(self, *url_args):
        crime = mock.Mock(spec=models.Schema)
        from ebpub.db.schemafilters import LocationFilter
        reverse_args = ('locations',) + url_args
        url = filter_reverse('crime', [reverse_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        filt = LocationFilter(req, context, None, *reverse_args[1:])
        return filt

    def test_filter__errors(self):
        self.assertRaises(FilterError, self._make_filter)

    def test_filter_by_location_choices(self):
        filt = self._make_filter('zipcodes')
        more_needed = filt.more_info_needed()
        self.assertEqual(more_needed['lookup_type'], u'ZIP Code')
        self.assertEqual(more_needed['lookup_type_slug'], 'zipcodes')
        self.assert_(len(more_needed['lookup_list']) > 0)

    @mock.patch('ebpub.db.schemafilters.models.Location.objects.filter')
    def test_filter_by_location__no_locations(self, mock_location_query):
        mock_location_query.return_value.order_by.return_value = []
        filt = self._make_filter('zipcodes')
        self.assertRaises(FilterError, filt.more_info_needed)
        try:
            filt.more_info_needed()
        except FilterError, e:
            self.assertEqual(str(e), "'empty lookup list'")

    def test_filter_by_location_detail(self):
        # TODO: this exercises a lot of implementation details; mock
        # more things to make it more isolated unit test?
        filt = self._make_filter('zipcodes', 'zip-1')
        filt.request.user= mock_with_attributes({'is_anonymous': lambda: True})
        self.assertEqual(filt.more_info_needed(), {})
        filt.apply()
        expected_loc = models.Location.objects.get(slug='zip-1')
        self.assertEqual(filt.context['place'], expected_loc)


class TestBlockFilter(TestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json',
                'wabash.yaml',
                )

    def _make_filter(self, *url_args):
        crime = mock.Mock(spec=models.Schema)
        from ebpub.db.schemafilters import BlockFilter
        reverse_args = ('streets',) + url_args
        url = filter_reverse('crime', [reverse_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        filt = BlockFilter(req, context, None, *reverse_args[1:])
        return filt

    def test_filter__errors(self):
        self.assertRaises(FilterError, self._make_filter)
        self.assertRaises(FilterError, self._make_filter, '')
        self.assertRaises(FilterError, self._make_filter, 'wabash-ave')
        # Bogus block range.
        self.assertRaises(FilterError, self._make_filter, 'wabash-ave', 'bogus', '8')
        # No block radius.
        self.assertRaises(FilterError, self._make_filter, 'wabash-ave', '200-298s')
        try:
            # Re-testing that last one so we can inspect the exception.
            self._make_filter('wabash-ave', '200-298s')
        except FilterError, e:
            import urllib
            self.assertEqual(urllib.quote(e.url), filter_reverse('crime', [('streets', 'wabash-ave', '200-298s', '8-blocks')]))


    @mock.patch('ebpub.db.schemafilters.get_metro')
    @mock.patch('ebpub.db.schemafilters.get_place_info_for_request')
    def test_filter__ok(self, mock_get_place_info, mock_get_metro): 
        def _mock_get_place_info(request, *args, **kwargs):
            block = mock_with_attributes(
                dict(from_num=99, to_num=100, street_slug='something',
                     pretty_name='99-100 something st'))
            return {'newsitem_qs': kwargs['newsitem_qs'],
                    'place': block,
                    'is_block': True,}

        mock_get_place_info.side_effect = _mock_get_place_info
        mock_get_metro.return_value = {'multiple_cities': True}
        filt = self._make_filter('boston', 'wabash-ave', '216-299n-s', '8')
        self.assertEqual(filt.more_info_needed(), {})
        filt.apply()
        self.assertEqual(filt.location_object.from_num, 99)
        self.assertEqual(filt.location_object.to_num, 100)
        self.assertEqual(filt.value, '8 blocks around 99-100 something st')

class TestDateFilter(TestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json', 'crimes.json'
                )

    def _make_filter(self, *url_args):
        crime = mock.Mock()
        from ebpub.db.schemafilters import DateFilter
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        self.mock_qs = mock.Mock()
        filt = DateFilter(req, context, self.mock_qs, *url_args[1:])
        return filt

    def test_filter__errors(self):
        self.assertRaises(FilterError, self._make_filter, '')
        self.assertRaises(FilterError, self._make_filter, 'by-date')
        self.assertRaises(FilterError, self._make_filter, 'by-date', 'bogus')
        self.assertRaises(FilterError, self._make_filter, 'by-date', 'bogus', 'bogus')
        self.assertRaises(FilterError, self._make_filter, 'by-date', '2011-04-07')

    def test_filter__ok(self):
        filt = self._make_filter('by-date', '2006-11-08', '2006-11-09')
        self.assertEqual(filt.more_info_needed(), {})
        filt.apply()
        self.assertEqual(filt.value, u'Nov. 8, 2006 \u2013 Nov. 9, 2006')
        self.assertEqual(self.mock_qs.filter.call_args, ((), filt.kwargs))


    def test_filter__ok__one_day(self):
        filt = self._make_filter('by-date', '2006-11-08', '2006-11-08')
        self.assertEqual(filt.more_info_needed(), {})
        filt.apply()
        self.assertEqual(filt.value, u'Nov. 8, 2006')
        self.assertEqual(self.mock_qs.filter.call_args, ((), filt.kwargs))

    def test_pub_date_filter(self):
        filt = self._make_filter('by-pub-date', '2006-11-08', '2006-11-09')
        from ebpub.db.schemafilters import PubDateFilter
        filt2 = PubDateFilter(filt.request, filt.context, filt.qs,
                              '2006-11-08', '2006-11-09')
        self.assertEqual(filt2.more_info_needed(), {})
        filt2.apply()
        self.assertEqual(filt2.argname, 'by-pub-date')
        self.assertEqual(filt2.date_field_name, 'pub_date')
        self.assertEqual(filt2.label, 'date published')
        self.assertEqual(self.mock_qs.filter.call_args, ((), filt2.kwargs))


class TestBoolFilter(TestCase):

    fixtures = ('crimes.json',)

    def _make_filter(self, *url_args):
        crime = mock.Mock()
        from ebpub.db.schemafilters import BoolFilter
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        sf_slug = url_args[0][3:]   # 'by-foo' -> 'foo'
        sf = models.SchemaField.objects.get(name=sf_slug)
        self.mock_qs = mock.Mock()
        filt = BoolFilter(req, context, self.mock_qs, *url_args[1:], schemafield=sf)
        return filt

    def test_filter__errors(self):
        self.assertRaises(FilterError, self._make_filter, 'by-arrests', 'maybe')
        self.assertRaises(FilterError, self._make_filter, 'by-arrests', 'maybe', 'no')

    def test_filter__ok(self):
        filt = self._make_filter('by-arrests', 'no')
        self.assertEqual(filt.more_info_needed(), {})
        filt.apply()
        self.assertEqual(self.mock_qs.by_attribute.call_args,
                         ((filt.schemafield, False), {}))
        self.assertEqual(filt.label, 'Arrests')
        self.assertEqual(filt.short_value, 'No')
        self.assertEqual(filt.value, 'Arrests: No')

    def test_filter__more_needed(self):
        filt = self._make_filter('by-arrests')
        more_needed = filt.more_info_needed()
        self.assertEqual(more_needed['lookup_type_slug'], 'arrests')


class TestLookupFilter(TestCase):

    fixtures = ('crimes.json',)

    def _make_filter(self, *url_args):
        crime = mock.Mock()
        from ebpub.db.schemafilters import LookupFilter
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        sf_slug = url_args[0][3:]   # 'by-foo' -> 'foo'
        sf = models.SchemaField.objects.get(name=sf_slug)
        self.mock_qs = mock.Mock()
        filt = LookupFilter(req, context, self.mock_qs, *url_args[1:], schemafield=sf)
        return filt

    def test_filter__errors(self):
        #self.assertRaises(FilterError, self._make_filter, 'by-beat', )
        self.assertRaises(FilterError, self._make_filter, 'by-beat', 'whoops')
        self.assertRaises(FilterError,
                          self._make_filter, 'by-beat', 'beat-9999')


    def test_filter__more_needed(self):
        filt = self._make_filter('by-beat')
        more_needed = filt.more_info_needed()
        self.assert_(more_needed)
        self.assertEqual(more_needed['lookup_type'], 'Beat')
        self.assertEqual(more_needed['lookup_type_slug'], 'beat')
        self.assertEqual(len(more_needed['lookup_list']), 2)

    def test_filter__ok(self):
        filt = self._make_filter('by-beat', 'beat-214', )
        filt = self._make_filter('by-beat', 'beat-214', )
        self.assertEqual(filt.more_info_needed(), {})
        filt.apply()
        self.assertEqual(filt.look.id, 1000)
        self.assertEqual(self.mock_qs.by_attribute.call_args,
                         ((filt.schemafield, filt.look.id), {}))
        self.assertEqual(filt.value, 'Police Beat 214')
        self.assertEqual(filt.short_value, 'Police Beat 214')
        self.assertEqual(filt.label, 'Beat')
        self.assertEqual(filt.argname, 'by-beat')

class TestTextFilter(TestCase):

    fixtures = ('crimes.json',)

    def _make_filter(self, *url_args):
        crime = mock.Mock()
        from ebpub.db.schemafilters import TextSearchFilter
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        sf_slug = url_args[0][3:]   # 'by-foo' -> 'foo'
        sf = models.SchemaField.objects.get(name=sf_slug)
        self.mock_qs = mock.Mock()
        filt = TextSearchFilter(req, context, self.mock_qs, *url_args[1:], schemafield=sf)
        return filt

    def test_filter__errors(self):
        self.assertRaises(FilterError, self._make_filter, 'by-status')

    def test_filter__ok(self):
        filt = self._make_filter('by-status', 'status 9-19')
        self.assertEqual(filt.more_info_needed(), {})
        filt.apply()
        self.assertEqual(self.mock_qs.text_search.call_count, 1)


class TestSchemaFilterChain(TestCase):

    def test_empty(self):
        from ebpub.db.schemafilters import SchemaFilterChain
        chain = SchemaFilterChain()
        self.assertEqual(chain.items(), [])

    def test_ordering(self):
        from ebpub.db.schemafilters import SchemaFilterChain
        chain = SchemaFilterChain()
        args = range(10)
        random.shuffle(args)
        for i in args:
            chain[i] = i
        self.assertEqual(chain.items(), [(i, i) for i in args])
        self.assertEqual(chain.keys(), args)

    def test_no_duplicates(self):
        from ebpub.db.schemafilters import SchemaFilterChain
        from ebpub.db.schemafilters import DuplicateFilterError
        chain = SchemaFilterChain()
        chain['foo'] = 'bar'
        self.assertRaises(DuplicateFilterError, chain.__setitem__, 'foo', 'bar')


    def test_normalized_ordering(self):
        from ebpub.db.schemafilters import SchemaFilterChain
        class Dummy(object):
            def __init__(self, sortkey):
                self._sort_key = sortkey

        dummies = [Dummy(i) for i in range(10)]
        random.shuffle(dummies)
        chain = SchemaFilterChain()
        for i in range(10):
            chain[i] = dummies[i]

        self.assertNotEqual(range(10),
                            [v._sort_key for v in chain.values()])

        normalized = chain.normalized_clone()
        self.assertEqual(range(10),
                         [v._sort_key for v in normalized.values()])


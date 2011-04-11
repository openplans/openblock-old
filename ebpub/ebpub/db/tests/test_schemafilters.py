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
from django.test import TestCase
from ebpub.db.views import filter_reverse
import mock

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


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
Unit tests for db.schemafilters.
"""

from ebpub.utils.testing import RequestFactory
from django.core import urlresolvers
from django.test import TestCase
from ebpub.db.schemafilters import FilterChain
from ebpub.db.schemafilters import FilterError
from ebpub.db.urlresolvers import filter_reverse
from ebpub.db.views import BadAddressException
from ebpub.db import models
import datetime
import mock
import random

class TestNewsitemFilter(TestCase):

    def test_getitem(self):
        from ebpub.db.schemafilters import NewsitemFilter
        fil = NewsitemFilter('dummy request', 'dummy context')
        fil.foo = 'bar'
        self.assertEqual(fil['foo'], 'bar')
        self.assertRaises(KeyError, fil.__getitem__, 'bar')


class TestIdFilter(TestCase):

    fixtures = ('test-schemafilter-views.json',)

    def test_validate(self):
        from ebpub.db.schemafilters import IdFilter
        fil = IdFilter(request=None, context={}, queryset=None)
        self.assertEqual(fil.validate(),
                         {'filter_key': 'id',
                          'option_list': [],
                          'param_label': 'id',
                          'param_name': 'id',
                          'select_multiple': True}
                         )

    def test_apply__no_ids(self):
        from ebpub.db.schemafilters import IdFilter
        fil = IdFilter(request=None, context={}, queryset=None, ids=[])
        self.assertEqual(list(fil.apply()), [])
        from ebpub.db.models import NewsItem
        self.assert_(NewsItem.objects.all().count() >= 1,
                     "we should have some items")

    def test_apply__some_ids(self):
        from ebpub.db.schemafilters import IdFilter
        from ebpub.db.models import NewsItem
        items = NewsItem.objects.all()[:2]
        self.assert_(len(items), "we should have some items")
        expected_ids = [item.id for item in items]
        fil = IdFilter(request=None, context={}, queryset=None,
                       ids=expected_ids)
        got_ids = [item.id for item in fil.apply()]
        self.assertEqual(sorted(expected_ids), sorted(got_ids))


class TestSchemaFilter(TestCase):

    fixtures = ('test-schemafilter-views.json',)

    def test_validate(self):
        from ebpub.db.schemafilters import SchemaFilter
        schema = models.Schema.objects.get(slug='crime')
        fil = SchemaFilter(request=None, context={}, queryset=None, schema=schema)
        self.assertEqual(fil.validate(), {})


    def test_apply(self):
        from ebpub.db.schemafilters import SchemaFilter
        schema = models.Schema.objects.get(slug='crime')
        fil = SchemaFilter(request=None, context={}, queryset=None, schema=schema)
        fil.apply()
        self.assert_(len(fil.qs) > 0)
        for item in fil.qs:
            self.assertEqual(item.schema.natural_key(), schema.natural_key())

    def test_apply__multi_schema(self):
        from ebpub.db.schemafilters import SchemaFilter
        schema = models.Schema.objects.get(slug='crime')
        fil = SchemaFilter(request=None, context={}, queryset=None,
                           schema=[schema, schema])
        fil.apply()
        self.assert_(len(fil.qs) > 0)
        for item in fil.qs:
            self.assertEqual(item.schema.natural_key(), schema.natural_key())


    @mock.patch('ebpub.db.schemafilters.get_schema_manager')
    def test_apply__with_request(self, mock_get_mgr):
        from ebpub.db.schemafilters import SchemaFilter
        schema = models.Schema.objects.get(slug='crime')
        request = mock.Mock()
        mock_get_mgr.return_value = models.Schema.objects
        fil = SchemaFilter(request=request, context={}, queryset=None,
                           schema=[schema, schema])
        fil.apply()
        self.assertEqual(mock_get_mgr.call_count, 1)


class TestLocationFilter(TestCase):

    # fixtures = ('test-locationtypes.json', 'test-locations.json',
    #             )
    fixtures = ('test-schemafilter-views.json',)


    def _make_filter(self, *url_args):
        crime = mock.Mock(spec=models.Schema)
        from ebpub.db.schemafilters import LocationFilter
        reverse_args = ('locations',) + url_args
        url = filter_reverse('crime', [reverse_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        filt = LocationFilter(req, context, None, *reverse_args[1:])
        return filt

    def test_filter__empty(self):
        self.assertRaises(FilterError, self._make_filter)

    def test_filter_by_location__choices(self):
        filt = self._make_filter('neighborhoods')
        more_needed = filt.validate()
        self.assertEqual(more_needed['filter_key'], u'location')
        self.assertEqual(more_needed['param_name'], 'locations')
        self.assertEqual(more_needed['param_label'], u'Neighborhood')
        self.assert_(len(more_needed['option_list']) > 0)
        self.assertEqual(filt.get_query_params(),
                         {'locations': 'neighborhoods'})

    @mock.patch('ebpub.db.schemafilters.models.Location.objects.filter')
    def test_filter_by_location__no_locations(self, mock_location_query):
        mock_location_query.return_value.order_by.return_value = []
        filt = self._make_filter('neighborhoods')
        self.assertRaises(FilterError, filt.validate)
        try:
            filt.validate()
        except FilterError, e:
            self.assertEqual(str(e), "'empty lookup list'")

    def test_filter_by_location_detail(self):
        # TODO: this exercises a lot of implementation details; mock
        # more things to make it more isolated unit test?
        filt = self._make_filter('neighborhoods', 'hood-1')
        filt.request.user = mock.Mock(is_anonymous=lambda: True)
        self.assertEqual(filt.validate(), {})
        filt.apply()
        expected_loc = models.Location.objects.get(slug='hood-1')
        self.assertEqual(filt.location_object, expected_loc)
        self.assertEqual(filt.get_query_params(),
                         {'locations': 'neighborhoods,hood-1'})
        # Items 1 & 2 should match this query because there's a corresponding
        # NewsItemLocation.
        self.assertEqual(sorted([item.id for item in filt.qs]),
                         [1, 2])


class TestBlockFilter(TestCase):

    fixtures = ('test-schemafilter-views.json',)

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


    @mock.patch('ebpub.db.schemafilters.get_metro')
    @mock.patch('ebpub.db.schemafilters.url_to_block')
    def test_filter__ok(self, mock_url_to_block, mock_get_metro):
        def _mock_url_to_block(request, *args, **kwargs):
            from django.contrib.gis.geos import Point
            block = mock.Mock(
                from_num=99, to_num=100, street_slug='something',
                pretty_name='99-100 something st',
                location=Point(60.0, 60.0),
                city='boston', left_city='boston',
                )
            block.number.return_value = '99-100'
            block.dir_url_bit.return_value = ''
            return block

        mock_url_to_block.side_effect = _mock_url_to_block
        mock_get_metro.return_value = {'multiple_cities': True}
        filt = self._make_filter('boston', 'wabash-ave', '216-299n-s', '8-blocks')
        self.assertEqual(filt.validate(), {})
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

    def test_filter__ok(self):
        filt = self._make_filter('by-date', '2006-11-08', '2006-11-09')
        self.assertEqual(filt.validate(), {})
        filt.apply()
        self.assertEqual(filt.value, u'Nov. 8, 2006 - Nov. 9, 2006')
        self.assertEqual(self.mock_qs.filter.call_args, ((), filt.kwargs))

    def test__single_arg_date(self):
        filt = self._make_filter('by-date', '2011-04-07')
        filt.apply()
        self.assertEqual(filt.value, u'April 7, 2011')


    def test_filter__ok__one_day(self):
        filt = self._make_filter('by-date', '2006-11-08', '2006-11-08')
        self.assertEqual(filt.validate(), {})
        filt.apply()
        self.assertEqual(filt.value, u'Nov. 8, 2006')
        self.assertEqual(self.mock_qs.filter.call_args, ((), filt.kwargs))

    def test_pub_date_filter(self):
        filt = self._make_filter('by-pubdate', '2006-11-08', '2006-11-09')
        from ebpub.db.schemafilters import PubDateFilter
        filt2 = PubDateFilter(filt.request, filt.context, filt.qs,
                              '2006-11-08', '2006-11-09')
        self.assertEqual(filt2.validate(), {})
        filt2.apply()
        self.assertEqual(filt2.date_field_name, 'pub_date')
        self.assertEqual(filt2.label, 'date published')
        self.assertEqual(self.mock_qs.filter.call_args, ((), filt2.kwargs))


class TestAttributeFilter(TestCase):

    def _mock_schemafield(self, name='mock-sf', pretty_name='Mock SF', **kwargs):
        # This is because the 'name' argument to mock.Mock
        # means something special, so we have to assign to it
        # after instantiation.
        sf = mock.Mock(pretty_name=pretty_name, **kwargs)
        sf.name = name
        return sf

    def test_init__no_args(self):
        from ebpub.db.schemafilters import AttributeFilter
        schemafield = self._mock_schemafield(name='mock-sf')
        qs = {}
        request = context = None
        filter = AttributeFilter(request, context, qs, schemafield=schemafield)
        self.assertEqual(filter.get_query_params(),
                         {'by-mock-sf': ''})


    def test_init__with_date(self):
        from ebpub.db.schemafilters import AttributeFilter
        schemafield = self._mock_schemafield(name='mock-sf')
        when = datetime.date(2009, 1, 23)
        qs = {}
        request = context = None
        filter = AttributeFilter(request, context, qs, when, schemafield=schemafield)
        self.assertEqual(filter.get_query_params(),
                         {'by-mock-sf': '2009-01-23'})

    def test_init__with_datetime(self):
        from ebpub.db.schemafilters import AttributeFilter
        schemafield = self._mock_schemafield(name='mock-sf')
        when = datetime.datetime(2009, 1, 23, 22, 40)
        qs = {}
        request = context = None
        filter = AttributeFilter(request, context, qs, when, schemafield=schemafield)
        self.assertEqual(filter.get_query_params(),
                         {'by-mock-sf': '2009-01-23T22:40:00'})

    def test_init__with_time(self):
        from ebpub.db.schemafilters import AttributeFilter
        schemafield = self._mock_schemafield(name='mock-sf')
        when = datetime.time(22, 40)
        qs = {}
        request = context = None
        filter = AttributeFilter(request, context, qs, when, schemafield=schemafield)
        self.assertEqual(filter.get_query_params(), 
                         {'by-mock-sf': '22:40:00'})


class TestBoolFilter(TestCase):

    fixtures = ('crimes.json',)

    def _make_filter(self, *url_args):
        crime = models.Schema.objects.get(slug='crime')
        from ebpub.db.schemafilters import BoolFilter
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        sf_name = url_args[0][3:]   # 'by-foo' -> 'foo'
        sf = models.SchemaField.objects.get(name=sf_name, schema=crime)
        self.mock_qs = mock.Mock()
        filt = BoolFilter(req, context, self.mock_qs, *url_args[1:], schemafield=sf)
        return filt

    def test_filter__errors(self):
        self.assertRaises(FilterError, self._make_filter, 'by-arrests', 'maybe')
        self.assertRaises(FilterError, self._make_filter, 'by-arrests', 'maybe', 'no')

    def test_filter__ok(self):
        filt = self._make_filter('by-arrests', 'no')
        self.assertEqual(filt.validate(), {})
        filt.apply()
        self.assertEqual(self.mock_qs.by_attribute.call_args,
                         ((filt.schemafield, False), {}))
        self.assertEqual(filt.label, 'Arrests')
        self.assertEqual(filt.short_value, 'No')
        self.assertEqual(filt.value, 'Arrests: No')

    def test_filter__more_needed(self):
        filt = self._make_filter('by-arrests')
        more_needed = filt.validate()
        self.assertEqual(more_needed['filter_key'], 'arrests')
        self.assertEqual(more_needed['param_name'], 'by-arrests')


class TestLookupFilter(TestCase):

    fixtures = ('crimes.json',)

    def _make_filter(self, *url_args):
        crime = mock.Mock()
        from ebpub.db.schemafilters import LookupFilter
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        sf_name, lookups = url_args[0], url_args[1:]
        sf_name = sf_name[3:]   # 'by-foo' -> 'foo'
        sf = models.SchemaField.objects.get(name=sf_name)
        self.mock_qs = mock.Mock()
        filt = LookupFilter(req, context, self.mock_qs, *lookups, schemafield=sf)
        return filt

    def test_filter__errors(self):
        #self.assertRaises(FilterError, self._make_filter, 'by-beat', )
        self.assertRaises(FilterError, self._make_filter, 'by-beat', 'whoops')
        self.assertRaises(FilterError,
                          self._make_filter, 'by-beat', 'beat-9999')


    def test_filter__more_needed(self):
        filt = self._make_filter('by-beat')
        more_needed = filt.validate()
        self.assert_(more_needed)
        self.assertEqual(more_needed['filter_key'], 'beat')
        self.assertEqual(more_needed['param_name'], 'by-beat')
        self.assertEqual(more_needed['param_label'], 'Beats')
        self.assert_(len(more_needed['option_list']) > 0)

    def test_filter__ok_single(self):
        filt = self._make_filter('by-beat', 'beat-214', )
        self.assertEqual(filt.validate(), {})
        filt.apply()
        self.assertEqual(filt.lookups[0].id, 214)
        self.assertEqual(self.mock_qs.by_attribute.call_args,
                         ((filt.schemafield, filt.lookups), {'is_lookup': True}))
        self.assertEqual(filt.value, 'Police Beat 214')
        self.assertEqual(filt.short_value, 'Police Beat 214')
        self.assertEqual(filt.label, 'Beat')
        self.assertEqual(filt.argname, 'by-beat')

    def test_filter__ok_multi(self):
        filt = self._make_filter('by-beat', 'beat-214', 'beat-64')
        self.assertEqual(filt.validate(), {})
        filt.apply()
        self.assertEqual(filt.lookups[0].id, 214)
        self.assertEqual(filt.lookups[1].id, 64)
        self.assertEqual(self.mock_qs.by_attribute.call_args,
                         ((filt.schemafield, filt.lookups), {'is_lookup': True}))
        self.assertEqual(filt.value, 'Police Beat 214, Police Beat 64')
        self.assertEqual(filt.short_value, 'Police Beat 214, Police Beat 64')
        self.assertEqual(filt.label, 'Beat')
        self.assertEqual(filt.argname, 'by-beat')
        self.assertEqual(filt.get_query_params(),
                         {'by-beat': 'beat-214,beat-64'})


class TestTextFilter(TestCase):

    fixtures = ('crimes.json',)

    def _make_filter(self, *url_args):
        crime = models.Schema.objects.get(slug='crime')
        from ebpub.db.schemafilters import TextSearchFilter
        url = filter_reverse('crime', [url_args])
        req = RequestFactory().get(url)
        context = {'schema': crime}
        sf_name = url_args[0][3:]   # 'by-foo' -> 'foo'
        sf = models.SchemaField.objects.get(name=sf_name, schema=crime)
        self.mock_qs = mock.Mock()
        filt = TextSearchFilter(req, context, self.mock_qs, *url_args[1:], schemafield=sf)
        return filt

    def test_filter__errors(self):
        self.assertRaises(FilterError, self._make_filter, 'by-status')

    def test_filter__ok(self):
        filt = self._make_filter('by-status', 'status 9-19')
        self.assertEqual(filt.validate(), {})
        filt.apply()
        self.assertEqual(self.mock_qs.text_search.call_count, 1)


class TestFilterChain(TestCase):

    def test_empty(self):
        chain = FilterChain()
        self.assertEqual(chain.items(), [])

    def test_ordering(self):
        chain = FilterChain()
        args = range(10)
        random.shuffle(args)
        for i in args:
            chain[i] = i
        self.assertEqual(chain.items(), [(i, i) for i in args])
        self.assertEqual(chain.keys(), args)

    def test_copy_and_mutate(self):
        schema = mock.Mock()
        chain = FilterChain(schema=schema)
        chain.lookup_descriptions.append(1)
        chain.base_url = 'http://xyz'
        chain['foo'] = 'bar'
        chain['qux'] = 'whee'
        clone = chain.copy()
        # Attributes are copied...
        self.assertEqual(clone.lookup_descriptions, [1])
        self.assertEqual(clone.base_url, chain.base_url)
        self.assertEqual(clone.schema, chain.schema, schema)
        # ... and mutating them doesn't affect the original.
        clone.lookup_descriptions.pop()
        self.assertEqual(chain.lookup_descriptions, [1])
        # Likewise, items are copied, and mutating doesn't affect the copy.
        self.assertEqual(clone['foo'], 'bar')
        del chain['foo']
        self.assertEqual(clone['foo'], 'bar')
        del clone['qux']
        self.assertEqual(chain['qux'], 'whee')
        # Likewise, clearing.
        clone.clear()
        self.assertEqual(clone.items(), [])
        self.assertEqual(chain['qux'], 'whee')

    def test_no_duplicates(self):
        from ebpub.db.schemafilters import DuplicateFilterError
        self.assertRaises(DuplicateFilterError, FilterChain,
                          (('foo', 'bar'), ('foo', 'bar2')))
        chain = FilterChain()
        chain['foo'] = 'bar'
        self.assertRaises(DuplicateFilterError, chain.__setitem__, 'foo', 'bar')

    def test_sort(self):
        class Dummy(object):
            def __init__(self, sort_value):
                self._sort_value = sort_value

        dummies = [Dummy(i) for i in range(10)]
        random.shuffle(dummies)
        chain = FilterChain()
        for i in range(10):
            chain[i] = dummies[i]

        self.assertNotEqual(range(10),
                            [v._sort_value for v in chain.values()])

        normalized = chain.copy()
        normalized.sort()
        self.assertEqual(range(10),
                         [v._sort_value for v in normalized.values()])


    def test_sort__real_filters(self):
        req = mock.Mock()
        qs = mock.Mock()
        schema = mock.Mock()
        context = {'newsitem_qs': qs, 'schema': schema}
        from ebpub.db.schemafilters import TextSearchFilter, BoolFilter
        from ebpub.db.schemafilters import LookupFilter, LocationFilter
        from ebpub.db.schemafilters import DateFilter

        def mock_schemafield(name):
            # mock.Mock(name='foo') does something magic, but I just
            # want to set the name attribute.
            sf = mock.Mock()
            sf.name = name
            return sf

        all_filters = [
            TextSearchFilter(req, context, qs, 'hi',
                             schemafield=mock_schemafield(name='mock text sf')),
            BoolFilter(req, context, qs, 'yes',
                       schemafield=mock_schemafield(name='mock bool sf')),
            LookupFilter(req, context, qs,
                         schemafield=mock_schemafield(name='mock lookup sf')),
            LocationFilter(req, context, qs, 'neighborhoods'),
            DateFilter(req, context, qs, '2011-04-11', '2011-04-12'),
            ]
        chain = FilterChain([(item.slug, item) for item in all_filters])
        ordered_chain = chain.copy()
        ordered_chain.sort()
        self.assertEqual(ordered_chain.keys(),
                         ['date', 'mock bool sf', 'location', 'mock lookup sf', 'mock text sf'])

    def test_filters_for_display(self):
        class Dummy(object):
            def __init__(self, label):
                self.label = label
        chain = FilterChain([('foo', Dummy('yes')),
                             ('bar', Dummy(None)),
                             ('bat', Dummy('yes also')),
                             ('baz', Dummy(None)),
                             ])
        self.assertEqual(len(chain.values()), 4)
        self.assertEqual(len(chain.filters_for_display()), 2)
        self.assert_(all([f.label for f in chain.filters_for_display()]))

    def test_add_date__whole_month(self):
        # Special syntax for adding a whole month, convenient for templates
        # where you don't want to have to calculate the end date.
        chain = FilterChain()
        import datetime
        chain.add('date', datetime.date(2011, 8, 13), 'month')
        self.assertEqual(chain['date'].start_date, datetime.date(2011, 8, 1))
        self.assertEqual(chain['date'].end_date, datetime.date(2011, 8, 31))

    def test_add__pubdate(self):
        # Key gets overridden.
        chain = FilterChain()
        import datetime
        chain.add('pubdate', datetime.date(2011, 8, 13))
        self.assert_(chain.has_key('date'))
        self.failIf(chain.has_key('pubdate'))
        self.assertEqual(chain['date'].start_date, datetime.date(2011, 8, 13))

    def test_add__bogus_keyword_arg(self):
        chain = FilterChain()
        self.assertRaises(TypeError, chain.add, 'date', '2011-01-1', foo='bar')

    def test_add__no_value(self):
        chain = FilterChain()
        self.assertRaises(FilterError, chain.add, 'date')

    def test_update_from_request__empty(self):
        request = mock.Mock()
        class StubQueryDict(dict):
            def getlist(self, key):
                return []
            def copy(self):
                return StubQueryDict(self.items())

        request.GET = StubQueryDict()
        chain = FilterChain(request=request)
        chain.update_from_request({})
        self.assertEqual(len(chain), 0)

    def test_add_by_place_id__bad(self):
        chain = FilterChain()
        from django.http import Http404
        self.assertRaises(Http404, chain.add_by_place_id, '')
        self.assertRaises(Http404, chain.add_by_place_id, 'blah')
        self.assertRaises(Http404, chain.add_by_place_id, 'b:123.1')
        self.assertRaises(Http404, chain.add_by_place_id, 'l:9999')

    @mock.patch('ebpub.utils.view_utils.get_object_or_404')
    def test_add_by_place_id(self, mock_get_object_or_404):
        chain = FilterChain()
        from ebpub.streets.models import Block
        from ebpub.db.schemafilters import BlockFilter
        block = Block(city='city', street_slug='street_slug',
                      pretty_name='pretty_name',
                      street_pretty_name='street_pretty_name',
                      street='street',
                      from_num='123', to_num='456',
                      )
        mock_get_object_or_404.return_value = block
        chain.add_by_place_id('b:123.1')
        self.assert_(isinstance(chain['location'], BlockFilter))

    def test_add__id(self):
        from ebpub.db.schemafilters import IdFilter
        chain = FilterChain()
        chain.add('id', [1, 2, 3])
        self.assert_(isinstance(chain['id'], IdFilter))


class TestUrlNormalization(TestCase):

    fixtures = ('test-schemafilter-views.json',)

    def setUp(self):
        super(TestUrlNormalization, self).setUp()
        self._patcher1 = mock.patch('ebpub.streets.models.proper_city')
        self.proper_city = self._patcher1.start()
        self.proper_city.return_value = 'chicago'
        self._patcher2 = mock.patch('ebpub.db.schemafilters.SmartGeocoder.geocode')
        self.mock_geocode = self._patcher2.start()

    def tearDown(self):
        self._patcher1.stop()
        self._patcher2.stop()
        super(TestUrlNormalization, self).tearDown()

    def _make_chain(self, url):
        request = RequestFactory().get(url)
        crime = models.Schema.objects.get(slug='crime')
        context = {'schema': crime}
        chain = FilterChain(request=request, context=context, schema=crime)
        chain.update_from_request(filter_sf_dict={})
        return chain

    def test_urls__ok(self):
        url = filter_reverse('crime',
                             [('streets', 'wabash-ave', '216-299n-s', '8-blocks'),])
        chain = self._make_chain(url)
        self.assertEqual(url, chain.make_url())

    def test_urls__intersection(self):
        url = urlresolvers.reverse(
            'ebpub-schema-filter', args=['crime']) + '?address=foo+and+bar'
        from ebpub.streets.models import Block, Intersection, BlockIntersection
        intersection = mock.Mock(spec=Intersection)
        blockintersection = mock.Mock(spec=BlockIntersection)
        blockintersection.block = Block.objects.get(street_slug='wabash-ave', from_num=216)
        intersection.blockintersection_set.all.return_value = [blockintersection]
        self.mock_geocode.return_value = {'intersection': intersection,
                                          'block': None}
        chain = self._make_chain(url)
        expected = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s', '8-blocks'),])
        result = chain.make_url()
        self.assertEqual(result, expected)

    def test_urls__bad_intersection(self):
        url = urlresolvers.reverse(
            'ebpub-schema-filter', args=['crime']) + '?address=foo+and+bar'
        from ebpub.streets.models import Block, Intersection, BlockIntersection
        intersection = mock.Mock(spec=Intersection)
        blockintersection = mock.Mock(spec=BlockIntersection)
        blockintersection.block = Block.objects.get(street_slug='wabash-ave', from_num=216)
        self.mock_geocode.return_value = {'intersection': intersection,
                                          'block': None}

        # Empty intersection list.
        intersection.blockintersection_set.all.return_value = []
        self.assertRaises(IndexError, self._make_chain, url)

        # Or, no block or intersection at all.
        self.mock_geocode.return_value = {'intersection': None, 'block': None}
        self.assertRaises(NotImplementedError, self._make_chain, url)


    def test_make_url__bad_address(self):
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime'])
        url += '?address=anything'  # doesn't matter because of mock_geocode

        from ebpub.geocoder.parser.parsing import ParsingError
        self.mock_geocode.side_effect = ParsingError()
        self.assertRaises(BadAddressException, self._make_chain, url)

        from ebpub.geocoder import GeocodingException
        self.mock_geocode.side_effect = GeocodingException()
        self.assertRaises(BadAddressException, self._make_chain, url)

        from ebpub.geocoder import AmbiguousResult
        self.mock_geocode.side_effect = AmbiguousResult(['foo', 'bar'])
        self.assertRaises(BadAddressException, self._make_chain, url)

    def test_make_url__address_query(self):
        from ebpub.streets.models import Block
        block = Block.objects.get(street_slug='wabash-ave', from_num=216)
        self.mock_geocode.return_value = {
            'city': block.left_city.title(),
            'zip': block.left_zip,
            'point': block.geom.centroid,
            'state': block.left_state,
            'intersection_id': None,
            'address': u'216 N Wabash Ave',
            'intersection': None,
            'block': block,
            }

        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime'])
        url += '?address=216+n+wabash+st&radius=8' # geocode result is mocked anyway.

        expected_url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n-s', '8-blocks'),])
        chain = self._make_chain(url)
        self.assertEqual(expected_url, chain.make_url())

    def test_make_url__bad_dates(self):
        from ebpub.db.views import BadDateException
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime'])
        # Error if either date is way too old.
        self.assertRaises(BadDateException, self._make_chain,
                          url + '?start_date=12/31/1899&end_date=01/01/2011')
        self.assertRaises(BadDateException, self._make_chain,
                          url + '?start_date=01/01/2011&end_date=12/31/1899')

        # Error if either date is not a parseable date.
        self.assertRaises(BadDateException, self._make_chain,
                          url + '?start_date=Whoops&end_date=01/01/2011')
        self.assertRaises(BadDateException, self._make_chain,
                          url + '?start_date=01/01/2011&end_date=Bzorch')


    def test_make_url__date_query(self):
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime'])
        url += '?start_date=2010/12/01&end_date=2011/01/01'
        chain = self._make_chain(url)
        expected = filter_reverse('crime', [('start_date', '2010-12-01'),
                                            ('end_date', '2011-01-01')])
        self.assertEqual(chain.make_url(), expected)

    def test_make_url__no_such_schemafield(self):
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime'])
        url += '?textsearch=foo&q=hello+goodbye'
        self.assertRaises(models.SchemaField.DoesNotExist,
                          self._make_chain, url)

    def test_make_url__textsearch_query(self):
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime'])
        url += '?textsearch=status&q=hello+goodbye'
        chain = self._make_chain(url)
        expected = filter_reverse('crime', [('by-status', 'hello goodbye')])
        self.assertEqual(chain.make_url(), expected)

    def test_make_url__preserves_other_query_params_sorted(self):
        url = filter_reverse('crime', [('start_date', '2011-04-05'),
                                       ('end_date', '2011-04-06')])
        url += '&textsearch=status&q=bar'
        # Add the extra params.
        url += '&zzz=yes&A=no'
        chain = self._make_chain(url)
        expected = filter_reverse('crime', [('start_date', '2011-04-05'),
                                            ('end_date', '2011-04-06'),
                                            ('by-status', 'bar')])
        # The extra params should end up sorted alphanumerically.
        expected = expected.replace('?', '?A=no&') + '&zzz=yes'
        self.assertEqual(chain.make_url(), expected)

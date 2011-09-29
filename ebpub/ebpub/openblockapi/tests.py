#   Copyright 2011 OpenPlans and contributors
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

"""
API tests
"""
import cgi
import datetime
import feedparser
import logging
import mock
import pytz
from django.contrib.gis import geos
from django.core.urlresolvers import reverse
from ebpub.utils.django_testcase_backports import TestCase
from django.utils import simplejson
from ebpub.db.models import Location, NewsItem, Schema
from ebpub.openblockapi import views
from ebpub.openblockapi.apikey import auth
from django.test.testcases import TransactionTestCase


class BaseTestCase(TestCase):
    def setUp(self):
        # Don't log 404 warnings, we expect a lot of them during these
        # tests.
        logger = logging.getLogger('django.request')
        self._previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        from ebpub.metros.allmetros import get_metro
        metro = get_metro()        
        self.old_multiple = metro['multiple_cities']
        self.old_city = metro['city_name']
        metro['multiple_cities'] = False
        metro['city_name'] = 'Boston'

    def tearDown(self):
        # Restore old log level.
        from ebpub.metros.allmetros import get_metro
        metro = get_metro()
        metro['multiple_cities'] = self.old_multiple
        metro['city_name'] = self.old_city

        logger = logging.getLogger('django.request')
        logger.setLevel(self._previous_level)



@mock.patch('ebpub.openblockapi.views.throttle_check', mock.Mock(return_value=0))
class TestAPI(BaseTestCase):

    fixtures = ('test-schema', 'test-locationtypes', 'test-locations')

    def test_api_available(self):
        response = self.client.get(reverse('check_api_available'))
        self.assertEqual(response.status_code, 200)

    def test_types_json(self):
        response = self.client.get(reverse('list_types_json'))
        self.assertEqual(response.status_code, 200)

        types = simplejson.loads(response.content)

        # The number of types includes any schemas loaded via
        # migrations or initial_data fixtures from ebpub.db *and* any
        # other apps in INSTALLED_APPS that load schemas. Ugh.
        self.assert_(len(types) >= 1, "no schemas loaded")

        t1 = types['test-schema']
        self.assertEqual(sorted(t1.keys()),
                         ['attributes',
                          'indefinite_article',
                          'last_updated',
                          'name',
                          'plural_name',
                          'slug',
                          ]
                         )
        self.assertEqual(t1['indefinite_article'], 'a')
        self.assertEqual(t1['last_updated'], '2007-12-10')
        self.assertEqual(t1['name'], 'Test schema item')
        self.assertEqual(t1['plural_name'], 'Test schema items')
        self.assertEqual(t1['slug'], 'test-schema')
        self.assertEqual(sorted(t1['attributes'].keys()),
                         ['bool', 'date', 'datetime', 'int', 'lookup',
                          'time', 'varchar',
                          ])
        self.assertEqual(t1['attributes']['varchar'],
                         {'pretty_name': 'Varchar', 'type': 'text',})
        self.assertEqual(t1['attributes']['lookup'],
                         {'pretty_name': 'Lookups', 'type': 'text'})
        self.assertEqual(t1['attributes']['bool'],
                         {'pretty_name': 'Bool', 'type': 'bool'})
        self.assertEqual(t1['attributes']['datetime'],
                         {'pretty_name': 'Datetime', 'type': 'datetime'})

    def test_jsonp(self):
        # Quick test that API endpoints are respecting the jsonp query
        # parameter.
        param = 'jsonp'
        wrapper = 'FooseBall'
        qs = '?%s=%s' % (param, wrapper)

        endpoints = [
            reverse('geocoder_api') + qs + '&q=Hood+1',
            reverse('items_json') + qs,
            reverse('list_types_json') + qs,
            reverse('locations_json') + qs,
            reverse('location_types_json') + qs,
            reverse('location_detail_json', kwargs={'slug': 'hood-1', 'loctype': 'neighborhoods'}) + qs,
        ]

        for e in endpoints:
            response = self.client.get(e)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content[:len(wrapper) + 1],
                             '%s(' % wrapper)
            self.assertEqual(response.content[-2:], ');')
            self.assertEqual(response.get('content-type', '')[:22],
                             'application/javascript')


    def test_items_redirect(self):
        url = reverse('items_index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'],
                         'http://testserver' + reverse('items_json'))

@mock.patch('ebpub.openblockapi.views.throttle_check', mock.Mock(return_value=0))
class TestPushAPI(BaseTestCase):

    fixtures = ('test-schema',)

    def _make_geojson(self, coords, **props):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point", "coordinates": coords,
                },
            "properties": props
            }


    @mock.patch('ebpub.openblockapi.views.check_api_authorization',
                mock.Mock(return_value=True))
    def test_create_basic(self):
        info = self._make_geojson(coords=[1.0, -1.0],
                                  description="Bananas!",
                                  title="All About Fruit",
                                  location_name="somewhere",
                                  url="http://example.com/bananas",
                                  item_date="2011-01-01",
                                  type="test-schema",
                                  )

        json = simplejson.dumps(info)
        url = reverse('items_index')
        response = self.client.post(url, json, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        new_item = NewsItem.objects.get(title='All About Fruit')
        self.assertEqual(
            response['location'],
            'http://testserver' + reverse('single_item_json', args=(), kwargs={'id_': new_item.id}))
        self.assertEqual(new_item.url, info['properties']['url'])
        # ... etc.


    def test_create__no_schema(self):
        info = self._make_geojson(coords=[1.0, 2.0])
        with self.assertRaises(views.InvalidNewsItem) as e:
            views._item_create(info)
        self.assertEqual(e.exception.errors,
                         {'type': 'schema None does not exist'})

    def test_create__no_geojson(self):
        info = {'type': 'ouchie'}
        with self.assertRaises(views.InvalidNewsItem) as e:
            views._item_create(info)
        self.assertEqual(e.exception.errors,
                         {'type': 'not a valid GeoJSON Feature'})

    def test_create__bad_dates(self):
        info = self._make_geojson(coords=[1.0, -1.0], type='test-schema',
                                  name='hello', title='hello title',
                                  description='hello descr', url='http://foo.com',
                                  item_date='ouch', location_name='here',
                                  )
        with self.assertRaises(views.InvalidNewsItem) as e:
            views._item_create(info)
        self.assertEqual(e.exception.errors,
                         {'item_date': [u'Enter a valid date.']})

    @mock.patch('ebpub.openblockapi.views._get_location_info')
    def test_create__missing_required_fields(self, mock_get_loc_info):
        mock_get_loc_info.return_value = (geos.Point(1,-1), 'somewhere')
        info = self._make_geojson(coords=[1.0, -1.0], type='test-schema')
        with self.assertRaises(views.InvalidNewsItem) as e:
            views._item_create(info)
        self.assertEqual(e.exception.errors,
                         {'description': [u'This field is required.'],
                          'title': [u'This field is required.'],
                          })

    @mock.patch('ebpub.openblockapi.views._get_location_info')
    def test_create_with_existing_lookups(self, mock_get_loc_info):
        mock_get_loc_info.return_value = (geos.Point(1,-1), 'somewhere')
        info = self._make_geojson(coords=[1.0, -1.0],
                                  lookup=['Lookup 7700 Name', 'Lookup 7701 Name'],
                                  type='test-schema',
                                  title='I have lookups', description='yes i do',
                                  url='http://foo.com',
                                  )
        views._item_create(info)
        item = NewsItem.objects.get(title='I have lookups')
        self.assertEqual(item.attributes['lookup'], u'7700,7701')


    @mock.patch('ebpub.openblockapi.views._get_location_info')
    def test_create_with_new_lookups(self, mock_get_loc_info):
        mock_get_loc_info.return_value = (geos.Point(1,-1), 'somewhere')
        info = self._make_geojson(coords=[1.0, -1.0],
                                  lookup=['Lookup 7702 Name', 'Lookup 7703 Name'],
                                  type='test-schema',
                                  title='I have lookups too', description='yes i do',
                                  url='http://foo.com',
                                  )
        views._item_create(info)
        item = NewsItem.objects.get(title='I have lookups too')
        self.assertEqual(item.attributes['lookup'], u'7702,7703')


@mock.patch('ebpub.openblockapi.views.throttle_check', mock.Mock(return_value=0))
class TestQuickAPIErrors(BaseTestCase):
    # Test errors that happen before filters get applied,
    # so, no fixtures needed.

    def test_jsonp__alphanumeric_only(self):
        import urllib
        params = {'jsonp': '()[]{};"<./,abc_XYZ_123~!@#$'}
        url = reverse('items_json') + '?' + urllib.urlencode(params)
        response = self.client.get(url)
        munged_value = 'abc_XYZ_123'
        self.assertEqual(response.content.strip()[:12], munged_value + '(')
        self.assertEqual(response.content.strip()[-2:], ');')


    def test_not_allowed(self):
        response = self.client.delete(reverse('items_index'))
        self.assertEqual(response.status_code, 405)
        response = self.client.put(reverse('items_index'))
        self.assertEqual(response.status_code, 405)

    @mock.patch('ebpub.openblockapi.views.LOCAL_TZ', pytz.timezone('US/Pacific'))
    def test_items_filter_date_invalid(self):
        qs = "?startdate=oops"
        response = self.client.get(reverse('items_json') + qs)
        self.assertContains(response, "Invalid start date", status_code=400)

        qs = "?enddate=oops"
        response = self.client.get(reverse('items_json') + qs)
        self.assertContains(response, "Invalid end date", status_code=400)

        # Atom too
        qs = "?enddate=oops"
        response = self.client.get(reverse('items_atom') + qs)
        self.assertContains(response, "Invalid end date", status_code=400)



@mock.patch('ebpub.openblockapi.views.LOCAL_TZ', pytz.timezone('US/Pacific'))
@mock.patch('ebpub.openblockapi.views.throttle_check', mock.Mock(return_value=0))
class TestItemSearchAPI(BaseTestCase):

    fixtures = ('test-item-search.json', 'test-schema.yaml')

    def tearDown(self):
        NewsItem.objects.all().delete()

    def test_single_item_json__notfound(self):
        id_ = '99999'
        response = self.client.get(reverse('single_item_json', kwargs={'id_': id_}))
        self.assertEqual(response.status_code, 404)

    def test_single_item_json(self):
        schema1 = Schema.objects.get(slug='type1')
        zone = 'US/Pacific'
        with self.settings(TIME_ZONE=zone):
            item = _make_items(1, schema1)[0]
            item.save()
            id_ = item.id
            response = self.client.get(reverse('single_item_json', kwargs={'id_': id_}))
            self.assertEqual(response.status_code, 200)
            out = simplejson.loads(response.content)
            self.assertEqual(out['type'], 'Feature')
            self.assert_('geometry' in out.keys())
            self.assertEqual(out['geometry']['type'], 'Point')
            self.assert_('properties' in out.keys())
            self.assertEqual(out['properties']['title'], item.title)
            self.assertEqual(out['properties']['description'], item.description)
            self.assertEqual(out['properties']['type'], schema1.slug)


    def test_items_nofilter(self):
        # create a few items
        schema1 = Schema.objects.get(slug='type1')
        schema2 = Schema.objects.get(slug='type2')
        items = []
        zone = 'US/Eastern'
        with self.settings(TIME_ZONE=zone):
            items += _make_items(5, schema1)
            items += _make_items(5, schema2)
            for item in items:
                item.save()

            response = self.client.get(reverse('items_json'))
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)

            assert len(ritems['features']) == len(items)

    def test_items_atom_nofilter(self):
        zone = 'America/Chicago'
        with self.settings(TIME_ZONE=zone):
            schema1 = Schema.objects.get(slug='type1')
            schema2 = Schema.objects.get(slug='type2')
            items = _make_items(5, schema1) + _make_items(5, schema2)
            for item in items:
                item.save()
            response = self.client.get(reverse('items_atom'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['content-type'], 'application/atom+xml')
            feed = feedparser.parse(response.content)
            self.assertEqual(feed['feed']['title'], u'openblock news item atom feed')
            self.assertEqual(len(feed['entries']), len(items))
            assert self._items_exist_in_xml_result(items, response.content)

    def test_items_filter_schema(self):
        zone = 'Asia/Dubai'
        with self.settings(TIME_ZONE=zone):
            # create a few items of each of two schema types
            schema1 = Schema.objects.get(slug='type1')
            schema2 = Schema.objects.get(slug='type2')
            items1 = _make_items(5, schema1)
            items2 = _make_items(5, schema2)
            for item in items1 + items2:
                item.save()

            # query for only the second schema
            response = self.client.get(reverse('items_json') + "?type=type2")
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)

            assert len(ritems['features']) == len(items2)
            for item in ritems['features']:
                assert item['properties']['type'] == 'type2'
            assert self._items_exist_in_result(items2, ritems)

    def test_items_atom_filter_schema(self):
        zone = 'Australia/North'
        with self.settings(TIME_ZONE=zone):
            # create a few items of each of two schema types
            schema1 = Schema.objects.get(slug='type1')
            schema2 = Schema.objects.get(slug='type2')
            items1 = _make_items(5, schema1)
            items2 = _make_items(5, schema2)
            for item in items1 + items2:
                item.save()

            # query for only the second schema
            response = self.client.get(reverse('items_atom') + "?type=type2")
            self.assertEqual(response.status_code, 200)
            feed = feedparser.parse(response.content)

            assert len(feed['entries']) == len(items2)
            for item in feed['entries']:
                # Yay feedparser, we don't know how it will spell the
                # openblock:type element, varies depending on... something.
                assert item.get('openblock_type', item.get('type')) == u'type2'


    def test_extension_fields_json(self):
        zone = 'Europe/Malta'
        with self.settings(TIME_ZONE=zone):
            schema = Schema.objects.get(slug='test-schema')

            ext_vals = {
                'varchar': ('This is a varchar', 'This is a varchar'), 
                'date': (datetime.date(2001, 01, 02), '2001-01-02'),
                'time': (datetime.time(hour=10, minute=11, second=12), 
                         '10:11:12-08:00'),
                'datetime': (datetime.datetime(2001, 01, 02, hour=10, minute=11, second=12),
                             '2001-01-02T10:11:12-08:00'),
                'bool': (True, True),
                'int': (7, 7),
                'lookup': ('7701,7700', ['Lookup 7701 Name', 'Lookup 7700 Name']),
            }

            items = _make_items(5, schema)
            for item in items:
                item.save()
                for k,v in ext_vals.items():
                    item.attributes[k] = v[0]

            response = self.client.get(reverse('items_json'))
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)

            self.assertEqual(len(ritems['features']), len(items))
            for item in ritems['features']:
                for k, v in ext_vals.items():
                    self.assertEqual(item['properties'][k], v[1])
            assert self._items_exist_in_result(items, ritems)


    def test_extension_fields_atom(self):
        zone = 'Pacific/Fiji'
        with self.settings(TIME_ZONE=zone):
            schema = Schema.objects.get(slug='test-schema')
            ext_vals = {
                'varchar': ('This is a varchar', 'This is a varchar'), 
                'date': (datetime.date(2001, 01, 02), '2001-01-02'),
                'time': (datetime.time(hour=10, minute=11, second=12), 
                         '10:11:12-08:00'),
                'datetime': (datetime.datetime(2001, 01, 02, hour=10, minute=11, second=12),
                             '2001-01-02T10:11:12-08:00'),
                'bool': (True, 'True'),
                'int': (7, '7'),
                'lookup': ('7700,7701', 'Lookup 7700 Name'),  # only check 1
            }

            items = _make_items(5, schema)
            for item in items:
                item.save()
                for k,v in ext_vals.items():
                    item.attributes[k] = v[0]

            response = self.client.get(reverse('items_atom'))
            self.assertEqual(response.status_code, 200)

            # Darn feedparser throws away nested extension elements. Gahhh.
            # Okay, let's parse the old-fashioned way.
            from lxml import etree
            root = etree.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom',
                  'openblock': 'http://openblock.org/ns/0'}

            entries = root.xpath('//atom:entry', namespaces=ns)
            assert len(entries) == len(items)
            for entry in entries:
                for key, value in sorted(ext_vals.items()):
                    attrs = entry.xpath(
                        'openblock:attributes/openblock:attribute[@name="%s"]' % key,
                        namespaces=ns)
                    if key == 'lookup':
                        self.assertEqual(len(attrs), 2)
                    else:
                        self.assertEqual(len(attrs), 1)
                    self.assertEqual(attrs[0].text, value[1])
            assert self._items_exist_in_xml_result(items, response.content)


    def test_items_filter_daterange_rfc3339(self):
        import pyrfc3339
        import pytz
        zone='US/Pacific'
        local_tz = pytz.timezone(zone)
        with self.settings(TIME_ZONE=zone):
            # create some items, they will have
            # dates spaced apart by one day, newest first
            schema1 = Schema.objects.get(slug='type1')
            items = _make_items(4, schema1)
            for item in items:
                item.save()

            # filter out the first and last item by constraining
            # the date range to the inner two items.
            # (Use local timezone for consistency with _make_items())
            startdate = pyrfc3339.generate(items[2].pub_date.replace(tzinfo=local_tz))
            enddate = pyrfc3339.generate(items[1].pub_date.replace(tzinfo=local_tz))
            # filter both ends
            qs = "?startdate=%s&enddate=%s" % (startdate, enddate)
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            self.assertEqual(len(ritems['features']), 2)
            assert self._items_exist_in_result(items[1:3], ritems)

            # startdate only
            qs = "?startdate=%s" % startdate
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == 3
            assert self._items_exist_in_result(items[:-1], ritems)

            # enddate only
            qs = "?enddate=%s" % enddate
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == 3
            assert self._items_exist_in_result(items[1:], ritems)

    def test_items_filter_daterange(self):
        zone = 'UTC'
        with self.settings(TIME_ZONE=zone):
            # create some items, they will have
            # dates spaced apart by one day, newest first
            schema1 = Schema.objects.get(slug='type1')
            items = _make_items(4, schema1)
            for item in items:
                cd = item.item_date
                item.pub_date = datetime.datetime(year=cd.year, month=cd.month, day=cd.day)
                item.save()

            # filter out the first and last item by constraining
            # the date range to the inner two items
            startdate = items[2].pub_date.strftime('%Y-%m-%d')
            enddate = items[1].pub_date.strftime('%Y-%m-%d')

            # filter both ends
            qs = "?startdate=%s&enddate=%s" % (startdate, enddate)
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == 2
            assert self._items_exist_in_result(items[1:3], ritems)

            # startdate only
            qs = "?startdate=%s" % startdate
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == 3
            assert self._items_exist_in_result(items[:-1], ritems)

            # enddate only
            qs = "?enddate=%s" % enddate
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == 3
            assert self._items_exist_in_result(items[1:], ritems)

    def test_items_limit_offset(self):
        zone = 'Europe/Vienna'
        with self.settings(TIME_ZONE=zone):
            # create a bunch of items
            schema1 = Schema.objects.get(slug='type1')
            items = _make_items(10, schema1)
            for item in items:
                item.save()

            # with no query, we should get all the items
            response = self.client.get(reverse('items_json'))
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == len(items)
            assert self._items_exist_in_result(items, ritems)

            # limited to 5, we should get the first 5
            qs = "?limit=5"
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == 5
            assert self._items_exist_in_result(items[:5], ritems)

            # offset by 2, we should get the last 8
            qs = "?offset=2"
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == 8
            assert self._items_exist_in_result(items[2:], ritems)

            # offset by 2, limit to 5
            qs = "?offset=2&limit=5"
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == 5
            assert self._items_exist_in_result(items[2:7], ritems)

    def test_items_predefined_location(self):
        zone = 'Europe/Zurich'
        with self.settings(TIME_ZONE=zone):
            # create a bunch of items
            schema1 = Schema.objects.get(slug='type1')
            items1 = _make_items(5, schema1)
            for item in items1:
                item.save()

            # make some items that are centered on a location
            loc = Location.objects.get(slug='hood-1')
            pt = loc.location.centroid
            items2 = _make_items(5, schema1)
            for item in items1:
                item.location = pt
                item.save()

            qs = "?locationid=%s" % cgi.escape("neighborhoods/hood-1")
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == 5
            assert self._items_exist_in_result(items2, ritems)


    def test_items_radius(self):
        zone = 'Asia/Saigon'
        with self.settings(TIME_ZONE=zone):
            # create a bunch of items
            schema1 = Schema.objects.get(slug='type1')
            items1 = _make_items(5, schema1)
            for item in items1:
                item.save()

            # make some items that are centered on a location
            loc = Location.objects.get(slug='hood-1')
            pt = loc.location.centroid
            items2 = _make_items(5, schema1)
            for item in items1:
                item.location = pt
                item.save()

            qs = "?center=%f,%f&radius=10" % (pt.x, pt.y)
            response = self.client.get(reverse('items_json') + qs)
            self.assertEqual(response.status_code, 200)
            ritems = simplejson.loads(response.content)
            assert len(ritems['features']) == 5
            assert self._items_exist_in_result(items2, ritems)


    def _items_exist_in_result(self, items, ritems):
        # XXX no ids for items :/
        all_titles = set([i['properties']['title'] for i in ritems['features']])
        for item in items:
            if not item.title in all_titles: 
                return False
        return True


    def _items_exist_in_xml_result(self, items, xmlstring):
        from lxml import etree
        root = etree.fromstring(xmlstring)
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'openblock': 'http://openblock.org/ns/0'}

        title_nodes = root.xpath('//atom:entry/atom:title', namespaces=ns)
        all_titles = set([t.text for t in title_nodes])
        for item in items:
            if not item.title in all_titles:
                return False
        return True

def _make_items(number, schema):
    items = []
    from django.conf import settings
    local_tz = pytz.timezone(settings.TIME_ZONE)
    curdate = datetime.datetime.now().replace(microsecond=0, tzinfo=local_tz)
    inc = datetime.timedelta(days=-1)
    for i in range(number):
        desc = '%s item %d' % (schema.slug, i)
        items.append(NewsItem(schema=schema, title=desc,
                              description=desc,
                              item_date=curdate.date(),
                              pub_date=curdate,
                              location=geos.Point(0,0)))
        curdate += inc
    return items

@mock.patch('ebpub.openblockapi.views.throttle_check', mock.Mock(return_value=0))
class TestGeocoderAPI(BaseTestCase):

    fixtures = ('test-locationtypes', 
                'test-locations.json',
                'test-placetypes.json',
                'test-places.json', 
                'test-streets.json',)

    def test_missing_params(self):
        response = self.client.get(reverse('geocoder_api'))
        self.assertEqual(response.status_code, 400)

    def test_address(self):
        qs = '?q=100+Adams+St'
        response = self.client.get(reverse('geocoder_api') + qs)
        self.assertEqual(response.status_code, 200)
        response = simplejson.loads(response.content)
        assert response['type'] == 'FeatureCollection'
        assert len(response['features']) == 1
        res = response['features'][0]
        assert res['geometry']['type'] == 'Point'
        assert res['properties']['type'] == 'address'
        assert res['properties']['address'] == '100 Adams St.'


    def test_address_notfound(self):
        qs = '?q=100+Nowhere+St'
        response = self.client.get(reverse('geocoder_api') + qs)
        self.assertEqual(response.status_code, 404)
        response = simplejson.loads(response.content)
        self.assertEqual(len(response['features']), 0)

    def test_intersection(self):
        qs = '?q=Adams+and+Chestnut'
        response = self.client.get(reverse('geocoder_api') + qs)
        self.assertEqual(response.status_code, 200)
        response = simplejson.loads(response.content)
        assert response['type'] == 'FeatureCollection'
        assert len(response['features']) == 1
        res = response['features'][0]
        assert res['geometry']['type'] == 'Point'
        assert res['properties']['type'] == 'address'
        assert res['properties']['address'] == 'Adams St. & Chestnut St.'

    def test_place(self):
        qs = '?q=Fake+Yards'
        response = self.client.get(reverse('geocoder_api') + qs)
        self.assertEqual(response.status_code, 200)
        response = simplejson.loads(response.content)
        assert response['type'] == 'FeatureCollection'
        assert len(response['features']) == 1
        res = response['features'][0]
        assert res['geometry']['type'] == 'Point'
        assert res['properties']['type'] == 'place'
        assert res['properties']['name'] == 'Fake Yards'

    def test_location(self):
        qs = '?q=Hood+1'
        response = self.client.get(reverse('geocoder_api') + qs)
        self.assertEqual(response.status_code, 200)
        response = simplejson.loads(response.content)
        assert response['type'] == 'FeatureCollection'
        assert len(response['features']) == 1
        res = response['features'][0]
        assert res['geometry']['type'] == 'Point'
        assert res['properties']['type'] == 'neighborhoods'
        assert res['properties']['name'] == 'Hood 1'


    def test_ambiguous(self):
        qs = '?q=Chestnut+and+Chestnut'
        response = self.client.get(reverse('geocoder_api') + qs)
        self.assertEqual(response.status_code, 200)
        response = simplejson.loads(response.content)
        assert response['type'] == 'FeatureCollection'
        assert len(response['features']) == 2

        names = set()
        for res in response['features']: 
            assert res['geometry']['type'] == 'Point'
            assert res['properties']['type'] == 'address'
            names.add(res['properties']['address'])

        assert "Chestnut Sq. & Chestnut Ave." in names
        assert "Chestnut Pl. & Chestnut Ave." in names


@mock.patch('ebpub.openblockapi.views.throttle_check', mock.Mock(return_value=0))
class TestLocationsAPI(BaseTestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json')

    def test_locations_json(self):
        response = self.client.get(reverse('locations_json'))
        self.assertEqual(response.status_code, 200)

        locations = simplejson.loads(response.content)
        self.assertEqual(type(locations), list)
        self.assertEqual(len(locations), 4)
        for loc in locations:
            self.assertEqual(sorted(loc.keys()),
                             ['city', 'description', 'id', 'name', 'slug', 'type', 'url'])
            self.assertEqual(loc['city'], 'boston')
            self.assert_(loc['type'] in ['zipcodes', 'neighborhoods'])
        self.assertEqual(locations[0]['slug'], 'zip-1')
        self.assertEqual(locations[0]['name'], 'Zip 1')

    def test_locations_json_by_type(self):
        qs = '?type=neighborhoods'
        response = self.client.get(reverse('locations_json') + qs)
        self.assertEqual(response.status_code, 200)
        locations = simplejson.loads(response.content)
        self.assertEqual(type(locations), list)
        self.assertEqual(len(locations), 2)
        for loc in locations:
            self.assertEqual(sorted(loc.keys()),
                             ['city', 'description', 'id', 'name', 'slug', 'type', 'url'])
            self.assertEqual(loc['city'], 'boston')
            self.assert_(loc['type'] == 'neighborhoods')
        self.assertEqual(locations[0]['slug'], 'hood-1')
        self.assertEqual(locations[0]['name'], 'Hood 1')

    def test_location_detail__invalid_type(self):
        response = self.client.get(reverse('location_detail_json', kwargs={'slug': 'hood-1', 'loctype': 'bogus'}))
        self.assertEqual(response.status_code,404)

    def test_location_detail__invalid_slug(self):
        response = self.client.get(reverse('location_detail_json', kwargs={'slug': 'bogus', 'loctype': 'neighborhoods'}))
        self.assertEqual(response.status_code,404)

    def _get_detail(self):
        url = reverse('location_detail_json', kwargs={'slug': 'hood-1', 'loctype': 'neighborhoods'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        detail = simplejson.loads(response.content)
        return detail

    def test_location_detail_json(self):
        detail = self._get_detail()
        self.assertEqual(type(detail), dict)
        self.assertEqual(sorted(detail.keys()), ['geometry', 'id', 'properties', 'type'])
        self.assertEqual(detail['type'], 'Feature')

    def test_location_detail_json__properties(self):
        detail = self._get_detail()
        props = detail['properties']
        self.assertEqual(type(props), dict)
        self.assertEqual(sorted(props.keys()),
                         ['area', 'centroid', 'city', 'description', 'name', 'openblock_type', 'population', 'slug', 'source', 'type'])
        self.assertEqual(type(props['area']), float)
        self.assert_(isinstance(props['city'], basestring))
        self.assert_(isinstance(props['description'], basestring))
        self.assertEqual(props['slug'], 'hood-1')
        self.assertEqual(props['name'], 'Hood 1')
        self.assertEqual(props['population'], None)
        self.assert_(props['centroid'].startswith('POINT ('))


    def test_location_detail_json__geometry(self):
        detail = self._get_detail()
        geom = detail['geometry']
        self.assertEqual(type(geom), dict)
        self.assertEqual(sorted(geom.keys()), ['coordinates', 'type'])
        self.assertEqual(geom['type'], 'MultiPolygon')
        coords = geom['coordinates'][0][0]
        self.assert_(len(coords), "No coordinates")
        for coord in coords:
            self.assertEqual(len(coord), 2)
            self.assertEqual(type(coord[0]), float)
            self.assertEqual(type(coord[1]), float)

    def test_location_types(self):
        response = self.client.get(reverse('location_types_json'))
        self.assertEqual(response.status_code, 200)
        types = simplejson.loads(response.content)
        self.assertEqual(len(types), 2)
        for typeinfo in types.values():
            self.assertEqual(sorted(typeinfo.keys()),
                             ['name', 'plural_name', 'scope'])
        t1 = types['neighborhoods']
        self.assertEqual(t1['name'], 'neighborhood')
        self.assertEqual(t1['plural_name'], 'neighborhoods')
        self.assertEqual(t1['scope'], 'boston')


@mock.patch('ebpub.openblockapi.views.throttle_check', mock.Mock(return_value=0))
class TestPlacesAPI(BaseTestCase):

    fixtures = ('test-placetypes.json', 'test-places.json')

    def test_place_types_json(self):
        response = self.client.get(reverse('place_types_json'))

        types = simplejson.loads(response.content)
        self.assertEqual(len(types), 2)
        for typeinfo in types.values():
            self.assertEqual(sorted(typeinfo.keys()),
                             ['geojson_url', 'name', 'plural_name'])
        t1 = types['poi']
        self.assertEqual(t1['name'], 'Point of Interest')
        self.assertEqual(t1['plural_name'], 'Points of Interest')

        t1 = types['police']
        self.assertEqual(t1['name'], 'Police Station')
        self.assertEqual(t1['plural_name'], 'Police Stations')

    def test_place_detail_json(self):
        response = self.client.get(reverse('place_detail_json', kwargs={'placetype': 'poi'}))
        places = simplejson.loads(response.content)
        self.assertEqual(len(places['features']), 2)

        names = set([x['properties']['name'] for x in places['features']])
        self.assertTrue('Fake Monument' in names)
        self.assertTrue('Fake Yards' in names)

        response = self.client.get(reverse('place_detail_json', kwargs={'placetype': 'police'}))
        places = simplejson.loads(response.content)
        self.assertEqual(len(places['features']), 2)

        names = set([x['properties']['name'] for x in places['features']])
        self.assertTrue('Faketown Precinct 1' in names)
        self.assertTrue('Faketown Precinct 2' in names)

    def test_place_detail_json__bogus_type(self):
        response = self.client.get(
            reverse('place_detail_json', kwargs={'placetype': 'Oops'}))
        self.assertEqual(response.status_code, 404)


@mock.patch('ebpub.openblockapi.views.throttle_check', mock.Mock(return_value=0))
class TestOpenblockAtomFeed(BaseTestCase):

    def test_root_attrs(self):
        from ebpub.openblockapi.views import OpenblockAtomFeed
        attrs = OpenblockAtomFeed('title', 'link', 'descr').root_attributes()
        self.assertEqual(attrs['xmlns:georss'], 'http://www.georss.org/georss')
        self.assertEqual(attrs['xmlns:openblock'], 'http://openblock.org/ns/0')

    # Not testing add_item_elements as it's an implementation detail
    # ... and, unlike root_attributes, is a pain to test.


class TestUtilFunctions(TestCase):

    def test_copy_nomulti(self):
        from ebpub.openblockapi.views import _copy_nomulti
        self.assertEqual(_copy_nomulti({}), {})
        self.assertEqual(_copy_nomulti({'a': 1}), {'a': 1})
        self.assertEqual(_copy_nomulti({'a': 1}), {'a': 1})
        self.assertEqual(_copy_nomulti({'a': [1], 'b': [1,2,3]}),
                         {'a': 1, 'b': [1,2,3]})


    def test_get_location_info(self):
        geom_dict = { "type": "Point", "coordinates": [100.0, 0.0] }
        geom, name = views._get_location_info(geom_dict, 'anywhere')
        self.assertEqual(geom.coords, (100.0, 0.0))
        self.assertEqual(name, 'anywhere')


    def test_check_api_auth__no_credentials(self):
        ip = '1.2.3.4'
        from django.core.exceptions import PermissionDenied
        request = mock.Mock(**{'user.is_authenticated.return_value': False,
                               'META': {'REMOTE_ADDR': ip},
                               'GET': {}, 'POST': {}})
        self.assertRaises(PermissionDenied, auth.check_api_authorization,
                          request)

    def test_check_api_auth__logged_in(self):
        ip = '1.2.3.4'
        request = mock.Mock(**{'user.is_authenticated.return_value': True,
                               'META': {'REMOTE_ADDR': ip},
                               'GET': {}, 'POST': {}})
        self.assertEqual(True, auth.check_api_authorization(request))

    def test_check_api_auth__key_invalid(self):
        from django.core.exceptions import PermissionDenied
        key = '12345'
        ip = '1.2.3.4'
        get_request = mock.Mock(**{'user.is_authenticated.return_value': False,
                                   'META': {'REMOTE_ADDR': ip,
                                            auth.KEY_HEADER: key},
                                   'GET': {}, 'POST': {}})
        self.assertRaises(PermissionDenied, auth.check_api_authorization,
                          get_request)


    def test_check_api_auth__key(self):
        from ebpub.openblockapi.apikey.models import generate_unique_api_key
        from ebpub.openblockapi.apikey.models import ApiKey
        from ebpub.accounts.models import User
        ip = '1.2.3.4'
        user = User.objects.create_user(email='bob@bob.com')
        key = ApiKey(key=generate_unique_api_key(), user=user)
        key.save()
        get_request = mock.Mock(**{'user.is_authenticated.return_value': False,
                                   'META': {'REMOTE_ADDR': ip,
                                            auth.KEY_HEADER: key},
                                   'session': mock.MagicMock(),
                                   'GET': {}, 'POST': {}})
        self.assertEqual(True, auth.check_api_authorization(get_request))

    @mock.patch('ebpub.openblockapi.views.throttle_check')
    def test_rest_view_decorator__allowed_methods(self, throttle_check):
        from ebpub.openblockapi.views import rest_view
        from django.http import HttpResponseNotAllowed
        throttle_check.return_value = False

        @rest_view(['HEAD', 'PUT'])
        def foo(request):
            return request.method

        request = mock.Mock(method='GET')

        result = foo(request)
        self.assert_(isinstance(result, HttpResponseNotAllowed))

        request.method = 'HEAD'
        self.assertEqual(foo(request), 'HEAD')
        request.method = 'PUT'
        self.assertEqual(foo(request), 'PUT')
        request.method = 'ANYTHING ELSE'
        result = foo(request)
        self.assert_(isinstance(result, HttpResponseNotAllowed))

    @mock.patch('ebpub.openblockapi.views.throttle_check')
    def test_rest_view_decorator__throttling(self, throttle_check):
        from ebpub.openblockapi.views import rest_view
        request = mock.Mock(method='GET')

        @rest_view(['GET'])
        def foo(request):
            return 'ok'

        throttle_check.return_value = 0
        self.assertEqual('ok', foo(request))

        throttle_check.return_value = 1234
        result = foo(request)
        self.assertEqual(result.status_code, 503)
        self.assertEqual(result['Retry-After'], '1234')


    @mock.patch('ebpub.openblockapi.throttle.cache')
    def test_cachethrottle(self, mock_cache):
        import time
        from ebpub.openblockapi.throttle import CacheThrottle
        throttle_at=25
        throttle = CacheThrottle(throttle_at=throttle_at)

        mock_cache.get.return_value = []
        self.assertEqual(False, throttle.should_be_throttled('some_id'))
        mock_cache.get.return_value = [int(time.time())] * (throttle_at - 1)
        self.assertEqual(False, throttle.should_be_throttled('some_id'))

        mock_cache.get.return_value = [int(time.time())] * throttle_at
        self.assertEqual(True, throttle.should_be_throttled('some_id'))
        mock_cache.get.return_value = [int(time.time())] * (throttle_at + 1)
        self.assertEqual(True, throttle.should_be_throttled('some_id'))

    @mock.patch('ebpub.openblockapi.views._throttle')
    def test_throttlecheck(self, mock_throttle):
        from ebpub.openblockapi.views import throttle_check

        request = mock.Mock(**{'user.is_authenticated.return_value': True,
                               'REQUEST.get.return_value': 'anything'})
        mock_throttle.should_be_throttled.return_value = True
        mock_throttle.seconds_till_unthrottling.return_value = 99
        self.assertEqual(99, throttle_check(request))

        request = mock.Mock(**{'user.is_authenticated.return_value': False,
                               'META': {auth.KEY_HEADER: 'test-api-key',}})
        self.assertEqual(99, throttle_check(request))

        self.assertEqual(mock_throttle.accessed.call_count, 0)
        mock_throttle.should_be_throttled.return_value = False
        self.assertEqual(0, throttle_check(request))
        self.assertEqual(mock_throttle.accessed.call_count, 1)


class TestMoreUtilFunctions(TransactionTestCase):

    # For things that mess with the db too much and need to be in a
    # transaction... eg. creating models on the fly and such
    # shenanigans.

    def test_is_instance_of_model(self):
        from django.contrib.gis.db import models
        class Foo(models.Model):
            class Meta:
                app_label = 'openblockapi'
        f = Foo()
        self.assertEqual(True, views.is_instance_of_model(f, Foo))
        self.assertRaises(TypeError, views.is_instance_of_model, f, Foo())


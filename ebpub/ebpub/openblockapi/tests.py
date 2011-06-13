"""
API tests
"""
import cgi
import datetime
import feedparser
import pytz
from django.contrib.gis import geos
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson
from ebpub.db.models import Location, NewsItem, Schema
from functools import wraps

import ebpub.openblockapi.views

def monkeypatch(obj, attrname, value):
    # Decorator for temporarily replacing an object
    # during a test, with an arbitrary value.
    # Unlike mock.patch, this allows the value to be
    # things other than mock.Mock objects.
    def patch(method):
        @wraps(method)
        def patched(*args, **kw):
            orig = getattr(obj, attrname)
            try:
                setattr(obj, attrname, value)
                return method(*args, **kw)
            finally:
                setattr(obj, attrname, orig)
        return patched
    return patch

class TestAPI(TestCase):

    fixtures = ('test-schema', 'test-locationtypes', 'test-locations')

    def test_api_available(self):
        response = self.client.get(reverse('check_api_available'))
        self.assertEqual(response.status_code, 200)

    def test_types_json(self):
        response = self.client.get(reverse('list_types_json'))
        self.assertEqual(response.status_code, 200)

        types = simplejson.loads(response.content)
        # This includes schemas from db/migrations/0007_load_default_schemas.py
        self.assertEqual(len(types), 8)
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
            assert response.content.startswith('%s(' % wrapper)
            assert response.content.endswith(");")
            assert response.get('content-type', None).startswith('application/javascript')

    def test_items_redirect(self):
        url = reverse('items_index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'],
                         'http://testserver' + reverse('items_json'))


class TestPushAPI(TestCase):

    fixtures = ('test-schema',)

    # def test_create_basic(self):
    #     #schema = Schema.objects.get(slug='test-schema')
    #     info = {
    #         "type": "Feature",
    #         "geometry": {
    #             "type": "Point",
    #             "coordinates": [1.0, -1.0]
    #             },
    #         "properties": {
    #             "description": "Bananas!",
    #             "title": "All About Fruit",
    #             "location_name": "somewhere",
    #             "url": "http://example.com/bananas",
    #             "item_date": "2011-01-01",
    #             "type": "test-schema",
    #             }
    #         }
    #     url = reverse('items_index')
    #     json = simplejson.dumps(info)
    #     response = self.client.post(url, json, content_type='application/json')
    #     self.assertEqual(response.status_code, 201)
    #     new_item = NewsItem.objects.get(title='All About Fruit')
    #     self.assertEqual(
    #         response['location'],
    #         'http://testserver' + reverse('single_item_json', args=(), kwargs={'id_': new_item.id}))
    #     self.assertEqual(new_item.url, info['properties']['url'])
    #     # ... etc.


class TestQuickAPIErrors(TestCase):
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

    @monkeypatch(ebpub.openblockapi.views, 'LOCAL_TZ', pytz.timezone('US/Pacific'))
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


class TestItemSearchAPI(TestCase):

    fixtures = ('test-item-search.json', 'test-schema.yaml')

    def tearDown(self):
        NewsItem.objects.all().delete()

    def test_single_item_json__notfound(self):
        id_ = '99999'
        response = self.client.get(reverse('single_item_json', kwargs={'id_': id_}))
        self.assertEqual(response.status_code, 404)

    def test_single_item_json(self):
        schema1 = Schema.objects.get(slug='type1')
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
        items += _make_items(5, schema1)
        items += _make_items(5, schema2)
        for item in items:
            item.save()

        response = self.client.get(reverse('items_json'))
        self.assertEqual(response.status_code, 200)
        ritems = simplejson.loads(response.content)

        assert len(ritems['features']) == len(items)

    def test_items_atom_nofilter(self):
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
            assert item['openblock_type'] == u'type2'


    # TODO: once DJango 1.4 is out, we might be able to remove this by
    # using # the TestCase.settings context manager as per
    # http://docs.djangoproject.com/en/dev/topics/testing/#overriding-settings
    @monkeypatch(ebpub.openblockapi.views, 'LOCAL_TZ', pytz.timezone('US/Pacific'))
    def test_extension_fields_json(self):
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


    @monkeypatch(ebpub.openblockapi.views, 'LOCAL_TZ', pytz.timezone('US/Pacific'))
    def test_extension_fields_atom(self):
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


    @monkeypatch(ebpub.openblockapi.views, 'LOCAL_TZ', pytz.timezone('US/Pacific'))
    def test_items_filter_daterange_rfc3339(self):
        import pyrfc3339
        import pytz
        from django.conf import settings
        # create some items, they will have
        # dates spaced apart by one day, newest first
        schema1 = Schema.objects.get(slug='type1')
        items = _make_items(4, schema1)
        for item in items:
            item.save()

        # filter out the first and last item by constraining
        # the date range to the inner two items.
        # (Use local timezone for consistency with _make_items())
        local_tz = pytz.timezone(settings.TIME_ZONE)
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

    @monkeypatch(ebpub.openblockapi.views, 'LOCAL_TZ', pytz.timezone('US/Pacific'))
    def test_items_filter_daterange(self):
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
        # create a bunch of items
        schema1 = Schema.objects.get(slug='type1')
        items1 = _make_items(5, schema1)
        for item in items1:
            item.save()

        # make some items that are centered on a location
        loc = Location.objects.get(slug='hood-1')
        pt = loc.centroid
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
        # create a bunch of items
        schema1 = Schema.objects.get(slug='type1')
        items1 = _make_items(5, schema1)
        for item in items1:
            item.save()

        # make some items that are centered on a location
        loc = Location.objects.get(slug='hood-1')
        pt = loc.centroid
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

class TestGeocoderAPI(TestCase):

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


class TestLocationsAPI(TestCase):

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
                         ['area', 'centroid', 'city', 'description', 'name', 'population', 'slug', 'source', 'type'])
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


class TestPlacesAPI(TestCase):

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

class TestOpenblockAtomFeed(TestCase):

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


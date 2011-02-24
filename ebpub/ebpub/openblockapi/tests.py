"""
API tests
"""
import cgi
import datetime
from django.contrib.gis import geos
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson
from ebpub.db.models import Location, NewsItem, Schema

class TestAPI(TestCase):

    fixtures = ('test-schema',)

    def test_api_available(self):
        response = self.client.get(reverse('check_api_available'))
        self.assertEqual(response.status_code, 200)

    def test_types_json(self):
        response = self.client.get(reverse('list_types_json'))
        self.assertEqual(response.status_code, 200)

        types = simplejson.loads(response.content)
        self.assertEqual(len(types), 1)
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
                         {'pretty_name': 'Datetime', 'type': 'datetime'}
)

class TestItemSearchAPI(TestCase):
    # XXX currently only testing GeoJSON API

    fixtures = ('test-item-search.json', )
    
    def tearDown(self):
        NewsItem.objects.all().delete()
    
    def test_items_nofilter(self):
        # create a few items
        schema1 = Schema.objects.get(slug='type1')
        schema2 = Schema.objects.get(slug='type2')
        items = []
        items += self._make_items(5, schema1)
        items += self._make_items(5, schema2)
        for item in items: 
            item.save()
        
        response = self.client.get(reverse('items_json'), status=200)
        ritems = simplejson.loads(response.content)
        
        assert len(ritems['features']) == len(items)

    def test_items_filter_schema(self):
        # create a few items of each of two schema types
        schema1 = Schema.objects.get(slug='type1')
        schema2 = Schema.objects.get(slug='type2')
        items1 = self._make_items(5, schema1)
        items2 = self._make_items(5, schema2)
        for item in items1 + items2:
            item.save()
        
        # query for only the second schema
        response = self.client.get(reverse('items_json') + "?type=type2", status=200)
        ritems = simplejson.loads(response.content)
        
        assert len(ritems['features']) == len(items2)
        for item in ritems['features']: 
            assert item['properties']['type'] == 'type2'
        assert self._items_exist_in_result(items2, ritems)

    def test_items_filter_daterange(self):
        # create some items, they will have 
        # dates spaced apart by one day, newest first
        schema1 = Schema.objects.get(slug='type1')
        items = self._make_items(4, schema1)
        for item in items: 
            item.save()
             
        # filter out the first and last item by constraining 
        # the date range to the inner two items
        startdate = items[2].item_date.strftime('%m%d%Y')
        enddate = items[1].item_date.strftime('%m%d%Y')

        # filter both ends
        qs = "?startdate=%s&enddate=%s" % (startdate, enddate)
        response = self.client.get(reverse('items_json') + qs, status=200)
        ritems = simplejson.loads(response.content)
        assert len(ritems['features']) == 2
        assert self._items_exist_in_result(items[1:3], ritems)

        # startdate only
        qs = "?startdate=%s" % startdate
        response = self.client.get(reverse('items_json') + qs, status=200)
        ritems = simplejson.loads(response.content)
        assert len(ritems['features']) == 3
        assert self._items_exist_in_result(items[:-1], ritems)
        
        # enddate only
        qs = "?enddate=%s" % enddate
        response = self.client.get(reverse('items_json') + qs, status=200)
        ritems = simplejson.loads(response.content)
        assert len(ritems['features']) == 3
        assert self._items_exist_in_result(items[1:], ritems)

    def test_items_limit_offset(self):
        # create a bunch of items
        schema1 = Schema.objects.get(slug='type1')
        items = self._make_items(10, schema1)
        for item in items: 
            item.save()

        # with no query, we should get all the items
        response = self.client.get(reverse('items_json'), status=200)
        ritems = simplejson.loads(response.content)
        assert len(ritems['features']) == len(items)
        assert self._items_exist_in_result(items, ritems)

        # limited to 5, we should get the first 5
        qs = "?limit=5"
        response = self.client.get(reverse('items_json') + qs, status=200)
        ritems = simplejson.loads(response.content)
        assert len(ritems['features']) == 5
        assert self._items_exist_in_result(items[:5], ritems)

        # offset by 2, we should get the last 8
        qs = "?offset=2"
        response = self.client.get(reverse('items_json') + qs, status=200)
        ritems = simplejson.loads(response.content)
        assert len(ritems['features']) == 8
        assert self._items_exist_in_result(items[2:], ritems)
        
        # offset by 2, limit to 5
        qs = "?offset=2&limit=5"
        response = self.client.get(reverse('items_json') + qs, status=200)
        ritems = simplejson.loads(response.content)
        assert len(ritems['features']) == 5
        assert self._items_exist_in_result(items[2:7], ritems)
        
        
    def test_items_predefined_location(self):
        # create a bunch of items
        schema1 = Schema.objects.get(slug='type1')
        items1 = self._make_items(5, schema1)
        for item in items1:
            item.save()            
        
        # make some items that are centered on a location
        loc = Location.objects.get(slug='hood-1')
        pt = loc.centroid
        items2 = self._make_items(5, schema1)
        for item in items1:
            item.location = pt
            item.save()
        
        qs = "?locationid=%s" % cgi.escape("neighborhoods/hood-1")
        response = self.client.get(reverse('items_json') + qs, status=200)
        ritems = simplejson.loads(response.content)
        assert len(ritems['features']) == 5
        assert self._items_exist_in_result(items2, ritems)
        

        
    def test_items_radius(self):
        # create a bunch of items
        schema1 = Schema.objects.get(slug='type1')
        items1 = self._make_items(5, schema1)
        for item in items1:
            item.save()            
        
        # make some items that are centered on a location
        loc = Location.objects.get(slug='hood-1')
        pt = loc.centroid
        items2 = self._make_items(5, schema1)
        for item in items1:
            item.location = pt
            item.save()
        
        qs = "?center=%f,%f&radius=10" % (pt.x, pt.y)
        response = self.client.get(reverse('items_json') + qs, status=200)
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

    def _make_items(self, number, schema): 
        items = []
        curdate = datetime.datetime.utcnow()
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
                'test-places.json', 
                'test-streets.json', )

    def test_address(self):
        qs = '?q=100+Adams+St'
        response = self.client.get(reverse('geocoder_api') + qs, status=200)
        response = simplejson.loads(response.content)
        assert response['type'] == 'FeatureCollection'
        assert len(response['features']) == 1
        res = response['features'][0]
        assert res['geometry']['type'] == 'Point'
        assert res['properties']['type'] == 'address'
        assert res['properties']['address'] == '100 Adams St.'

    def test_intersection(self):
        qs = '?q=Adams+and+Chestnut'
        response = self.client.get(reverse('geocoder_api') + qs, status=200)
        response = simplejson.loads(response.content)
        assert response['type'] == 'FeatureCollection'
        assert len(response['features']) == 1
        res = response['features'][0]
        assert res['geometry']['type'] == 'Point'
        assert res['properties']['type'] == 'address'
        assert res['properties']['address'] == 'Adams St. & Chestnut St.'

    def test_place(self):
        qs = '?q=Fake+Yards'
        response = self.client.get(reverse('geocoder_api') + qs, status=200)
        response = simplejson.loads(response.content)
        assert response['type'] == 'FeatureCollection'
        assert len(response['features']) == 1
        res = response['features'][0]
        assert res['geometry']['type'] == 'Point'
        assert res['properties']['type'] == 'place'
        assert res['properties']['name'] == 'Fake Yards'

    def test_location(self):
        qs = '?q=Hood+1'
        response = self.client.get(reverse('geocoder_api') + qs, status=200)
        response = simplejson.loads(response.content)
        assert response['type'] == 'FeatureCollection'
        assert len(response['features']) == 1
        res = response['features'][0]
        assert res['geometry']['type'] == 'Point'
        assert res['properties']['type'] == 'neighborhoods'
        assert res['properties']['name'] == 'Hood 1'

        
    # def test_ambiguous(self):
    #     raise NotImplementedError

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
                             ['city', 'description',  'name', 'slug', 'type', 'url'])
            self.assertEqual(loc['city'], 'boston')
            self.assert_(loc['type'] in ['zipcodes', 'neighborhoods'])
        self.assertEqual(locations[0]['slug'], 'zip-1')
        self.assertEqual(locations[0]['name'], 'Zip 1')


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
        self.assertEqual(sorted(detail.keys()), ['geometry', 'properties', 'type'])
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

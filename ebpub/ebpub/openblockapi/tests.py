"""
API tests
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import simplejson

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

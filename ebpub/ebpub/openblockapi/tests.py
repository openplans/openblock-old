"""
API tests
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import simplejson

class TestAPI(TestCase):

    fixtures = ['test-schema']

    def test_api_available(self):
        self.client.get(reverse('check_api_available'), status=200)

    def test_types_json(self):
        output = self.client.get(reverse('list_types_json'), status=200)
        types = simplejson.loads(output.content)
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


    def test_locations_json(self):
        raise NotImplementedError

    def test_location_detail_json(self):
        raise NotImplementedError

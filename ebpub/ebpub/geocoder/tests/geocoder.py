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

from ebpub.geocoder import SmartGeocoder, AmbiguousResult, InvalidBlockButValidStreet, DoesNotExist
import django.test
import mock


class TestSmartGeocoder(django.test.TestCase):
    fixtures = ['wabash.yaml']

    def setUp(self):
        self.geocoder = SmartGeocoder(use_cache=False)

    @mock.patch('ebpub.streets.models.get_metro')
    def test_address_geocoder(self, mock_get_metro):
        mock_get_metro.return_value = {'city_name': 'CHICAGO',
                                       'multiple_cities': False}
        result = self.geocoder.geocode('200 S Wabash Ave')
        self.assertEqual(result['city'], 'Chicago')
        self.assertEqual(result['address'], '200 S Wabash Ave.')

    @mock.patch('ebpub.streets.models.get_metro')
    def test_address_geocoder__wrong_suffix_works(self, mock_get_metro):
        mock_get_metro.return_value = {'city_name': 'CHICAGO',
                                       'multiple_cities': False}
        result = self.geocoder.geocode('220 S Wabash St')
        self.assertEqual(result['address'], '220 S Wabash Ave.')
        # Or none at all.
        result = self.geocoder.geocode('220 S Wabash')
        self.assertEqual(result['address'], '220 S Wabash Ave.')

    @mock.patch('ebpub.streets.models.get_metro')
    def test_address_geocoder_ambiguous(self, mock_get_metro):
        mock_get_metro.return_value = {'city_name': 'CHICAGO',
                                       'multiple_cities': False}
        # Ambiguous because of missing pre_dir.
        self.assertRaises(AmbiguousResult, self.geocoder.geocode, '220 Wabash')

    def test_address_geocoder_invalid_block(self):
        self.assertRaises(InvalidBlockButValidStreet,
                          self.geocoder.geocode, '100000 S Wabash')

    @mock.patch('ebpub.streets.models.get_metro')
    def test_block_geocoder(self, mock_get_metro):
        mock_get_metro.return_value = {'city_name': 'CHICAGO',
                                       'multiple_cities': False}
        address = self.geocoder.geocode('200 block of Wabash')
        self.assertEqual(address['city'], 'Chicago')

    def test_intersection_geocoder(self):
        address = self.geocoder.geocode('Wabash and Jackson')
        self.assertEqual(address['city'], 'CHICAGO')


class TestFullGeocode(django.test.TestCase):

    fixtures = ['wabash.yaml', 'places.yaml']

    def test_full_geocode_place(self):
        from ebpub.geocoder.base import full_geocode
        place = full_geocode('Sears Tower', search_places=True)
        self.assertEqual(place['type'], 'place')
        self.assertEqual(place['result'].normalized_name, 'SEARS TOWER')

    def test_full_geocode__no_place(self):
        from ebpub.geocoder.base import full_geocode, DoesNotExist
        self.assertRaises(DoesNotExist, full_geocode, 'Bogus Place Name')

    def test_full_geocode__bad_block_on_good_street(self):
        from ebpub.geocoder.base import full_geocode
        # This block goes up to 298.
        result = full_geocode('299 S. Wabash Ave.', convert_to_block=False)
        self.assert_(result['ambiguous'])
        self.assertEqual(result['type'], 'block')
        self.assertEqual(result['street_name'], 'Wabash Ave.')
        self.assertEqual(len(result['result']), 3)

    def test_full_geocode__convert_to_block(self):
        from ebpub.geocoder.base import full_geocode
        # This block goes up to 298.
        result = full_geocode('299 S. Wabash Ave.', convert_to_block=True)
        self.failIf(result['ambiguous'])
        self.assertEqual(result['type'], 'block')
        self.assertEqual(result['result']['address'], '200 block of S. Wabash Ave.')
        # This is also the default behavior.
        self.assertEqual(result, full_geocode('299 S. Wabash Ave.'))


class TestDisambiguation(django.test.TestCase):

    def test_disambiguate__no_args(self):
        from ebpub.geocoder.base import disambiguate
        self.assertEqual(disambiguate([]), [])
        self.assertEqual(disambiguate([]), [])

    def test_disambiguate__guess(self):
        from ebpub.geocoder.base import disambiguate
        # 'guess' doesn't do anything unless we have something to filter on.
        self.assertEqual(disambiguate([], zipcode="10014", guess=True),
                         [])
        self.assertEqual(disambiguate([{1:1}], zipcode="10014", guess=True),
                         [{1:1}])
        self.assertEqual(disambiguate([{1:1}, {2:2}, {3:3}], zipcode="10014", guess=True),
                         [{1:1}])

    def test_disambiguate__city(self):
        from ebpub.geocoder.base import disambiguate
        input_results = [{'name': 'bob', 'city': 'Brooklyn'},
                         {'name': 'bob', 'city': 'Manchester'},
                         {'name': 'bob', 'city': 'Oslo'},
                         {'name': 'joe', 'city': 'Oslo'},
                         ]
        self.assertEqual(disambiguate(input_results, city='Some Other City'),
                         input_results)
        self.assertEqual(disambiguate(input_results, city='Brooklyn'),
                         [{'name': 'bob', 'city': 'Brooklyn'}])
        self.assertEqual(disambiguate(input_results, city='Oslo'),
                         [{'name': 'bob', 'city': 'Oslo'},
                          {'name': 'joe', 'city': 'Oslo'}])
        self.assertEqual(disambiguate(input_results, city='Oslo', guess=True),
                         [{'name': 'bob', 'city': 'Oslo'}])


    def test_disambiguate__state(self):
        from ebpub.geocoder.base import disambiguate
        input_results = [{'name': 'bob', 'state': 'MA'},
                         {'name': 'bob', 'state': 'TN'},
                         {'name': 'bob', 'state': 'WA'},
                         {'name': 'joe', 'state': 'WA'},
                         ]
        self.assertEqual(disambiguate(input_results, state='Some Other State'),
                         input_results)
        self.assertEqual(disambiguate(input_results, state='WA'),
                         [{'name': 'bob', 'state': 'WA'},
                          {'name': 'joe', 'state': 'WA'},
                          ])

    def test_disambiguate__zip(self):
        from ebpub.geocoder.base import disambiguate
        input_results = [{'name': 'bob', 'zip': '12345'},
                         {'name': 'bob', 'zip': '67890'},
                         {'name': 'bob', 'zip': '55555'},
                         {'name': 'joe', 'zip': '55555'},
                         ]
        self.assertEqual(disambiguate(input_results, zipcode='Some Other Zipcode'),
                         input_results)
        self.assertEqual(disambiguate(input_results, zipcode='67890'),
                         [{'name': 'bob', 'zip': '67890'},])
        # You can spell it either 'zipcode' or 'zip'.
        self.assertEqual(disambiguate(input_results, zip='67890'),
                         [{'name': 'bob', 'zip': '67890'},])


    def test_disambiguate__all(self):
        from ebpub.geocoder.base import disambiguate
        input_results = [
            {'name': 'bob', 'city': 'C1', 'state': 'S2', 'zip': 'Z1'},
            {'name': 'bob', 'city': 'C1', 'state': 'S1', 'zip': 'Z1'},
            {'name': 'bob', 'city': 'C1', 'state': 'S1', 'zip': 'Z2'},
            {'name': 'bob', 'city': 'C2', 'state': 'S1', 'zip': 'Z1'},
            {'name': 'bob', 'city': 'C2', 'state': 'S1', 'zip': 'Z1', 'suffix': 'SF1'},
            ]
        self.assertEqual(disambiguate(input_results, city='C1', state='S1', zipcode='Z1'),
                         [{'name': 'bob', 'city': 'C1', 'state': 'S1', 'zip': 'Z1'}])

        # We could pass other args, eg. 'suffix', although
        # in practice this would require those keys to be present in Address dicts.
        self.assertEqual(disambiguate(input_results, suffix='SF1'),
                         [{'name': 'bob', 'city': 'C2', 'state': 'S1', 'zip': 'Z1', 'suffix': 'SF1'}])



if __name__ == '__main__':
    pass

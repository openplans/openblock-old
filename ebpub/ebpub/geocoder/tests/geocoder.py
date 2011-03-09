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

from ebpub.geocoder import SmartGeocoder, AmbiguousResult, InvalidBlockButValidStreet
import os.path
import unittest
import django.test
import yaml
import mock

class GeocoderTestCase(unittest.TestCase):
    address_fields = ('address', 'city', 'zip')

    def load_fixtures(self):
        fixtures_filename = 'locations.yaml'
        locations = yaml.load(open(os.path.join(os.path.dirname(__file__), fixtures_filename)))
        for key, value in locations.items():
            pass

    def assertAddressMatches(self, expected, actual):
        unmatched_fields = []

        for field in self.address_fields:
            try:
                self.assertEqual(expected[field], actual[field])
            except AssertionError, e:
                unmatched_fields.append(field)

        if unmatched_fields:
            raise AssertionError('unmatched address fields: %s' % ', '.join(unmatched_fields))

    def assertNearPoint(self, point, other):
        try:
            self.assertAlmostEqual(point.x, other.x, places=3)
            self.assertAlmostEqual(point.y, other.y, places=3)
        except AssertionError, e:
            raise AssertionError('`point\' not near enough to `other\': %s', e)

class BaseGeocoderTestCase(django.test.TestCase):
    fixtures = ['wabash.yaml']

    def setUp(self):
        self.geocoder = SmartGeocoder(use_cache=False)

    @mock.patch('ebpub.streets.models.get_metro')
    def test_address_geocoder(self, mock_get_metro):
        mock_get_metro.return_value = {'city_name': 'CHICAGO',
                                       'multiple_cities': False}
        address = self.geocoder.geocode('200 S Wabash')
        self.assertEqual(address['city'], 'Chicago')

    @mock.patch('ebpub.streets.models.get_metro')
    def test_address_geocoder_ambiguous(self, mock_get_metro):
        mock_get_metro.return_value = {'city_name': 'CHICAGO',
                                       'multiple_cities': False}
        self.assertRaises(AmbiguousResult, self.geocoder.geocode, '220 Wabash')

    def test_address_geocoder_invalid_block(self):
        self.assertRaises(InvalidBlockButValidStreet, self.geocoder.geocode, '100000 S Wabash')

    @mock.patch('ebpub.streets.models.get_metro')
    def test_block_geocoder(self, mock_get_metro):
        mock_get_metro.return_value = {'city_name': 'CHICAGO',
                                       'multiple_cities': False}
        address = self.geocoder.geocode('200 block of Wabash')
        self.assertEqual(address['city'], 'Chicago')

    def test_intersection_geocoder(self):
        address = self.geocoder.geocode('Wabash and Jackson')
        self.assertEqual(address['city'], 'CHICAGO')

if __name__ == '__main__':
    pass

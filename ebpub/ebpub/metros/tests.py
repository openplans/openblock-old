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

from django.test import TestCase
from django.contrib.gis.geos import Point
from ebpub.metros.models import Metro
import logging

pt_in_chicago = Point((-87.68489561595398, 41.852929331184384)) # point in center of Chicago
pt_in_chi_bbox = Point((-87.83384627077956, 41.85365447332586)) # point just west of Chicago's border but due south of O'Hare
pt_in_lake_mi = Point((-86.99514699540548, 41.87468001919902)) # point way out in Lake Michigan

class MetroTest(TestCase):
    fixtures = ['metros.json']

    def test_point_in_metro(self):
        # Tests finding a metro with a point contained by its boundary
        self.assertEquals(Metro.objects.containing_point(pt_in_chicago).name, 'Chicago')

    def test_point_in_bbox_not_in_metro(self):
        # Tests with a point in the metro's bounding box but not in its boundary
        self.assertRaises(Metro.DoesNotExist, Metro.objects.containing_point, pt_in_chi_bbox)

    def test_point_not_in_metro(self):
        # Tests with a point not in any metro
        self.assertRaises(Metro.DoesNotExist, Metro.objects.containing_point, pt_in_lake_mi)

class MetroViewsTest(TestCase):
    fixtures = ['metros.json']

    # De-hardcoding ebpub's URLs means that to test 404 pages, we need
    # ebpub's URL config or else the 404 page blows up with NoReverseMatch.
    # So, cook up a URL config that includes both.
    urls = 'ebpub.metros.test_urls'

    def setUp(self):
        # Don't log 404 warnings, we expect a lot of them during these
        # tests.
        logger = logging.getLogger('django.request')
        self._previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

    def tearDown(self):
        # Restore old log level.
        logger = logging.getLogger('django.request')
        logger.setLevel(self._previous_level)

    def test_lookup_metro_success(self):
        # Tests getting a successful JSON response from a lng/lat query
        response = self.client.get('/metros/lookup/', {'lng': pt_in_chicago.x, 'lat': pt_in_chicago.y})
        self.assertContains(response, 'Chicago', status_code=200)
        self.assertEqual(response['content-type'], 'application/javascript')

    def test_lookup_metro_in_bbox_fails(self):
        # Tests getting a 404 from a lng/lat query not quite in the metro
        response = self.client.get('/metros/lookup/', {'lng': pt_in_chi_bbox.x, 'lat': pt_in_chi_bbox.y})
        self.assertEqual(response.status_code, 404)

    def test_lookup_metro_fails(self):
        # Tests getting a 404 from a lng/lat query not in any metro
        response = self.client.get('/metros/lookup/', {'lng': pt_in_lake_mi.x, 'lat': pt_in_lake_mi.y})
        self.assertEqual(response.status_code, 404)

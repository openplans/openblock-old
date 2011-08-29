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

from django.http import Http404
from django.test import TestCase
from ebpub.constants import BLOCK_RADIUS_CHOICES
from ebpub.db.models import Location, LocationType
from ebpub.streets.models import Block
from ebpub.utils.view_utils import make_pid
from ebpub.utils.view_utils import parse_pid
import unittest

LINESTRING = 'LINESTRING (0.0 0.0, 1.0 1.0)'

class PidTests(TestCase):


    def _makeLocation(self):
        location = Location(
            location_type=self.loctype, display_order=1,
            slug='testloc', name='testloc', normalized_name='testloc',
            city='city', source='source', is_public=True)
        location.save()
        return location

    def setUp(self):
        # can't make a Location without a LocationType
        loctype = LocationType(name='testloctype', plural_name='xs', slug='x',
                               is_browsable=False, is_significant=False)
        loctype.save()
        self.loctype = loctype

    def _makeBlock(self):
        block = Block(geom=LINESTRING)
        block.save()
        return block

    def test_parse_pid__invalid(self):
        self.assertRaises(Http404, parse_pid, 'xyz')
        self.assertRaises(Http404, parse_pid, 'c:99.1')
        self.assertRaises(Http404, parse_pid, 'b:x')

    def test_parse_pid__block(self):
        b = self._makeBlock()
        result = parse_pid('b:%d.1' % b.id)
        self.assertEqual(result, (b, '1', BLOCK_RADIUS_CHOICES['1']))

    def test_parse_pid__block__invalid_radius(self):
        b = self._makeBlock()
        self.assertRaises(Http404, parse_pid, 'b:%d.27' % b.id)

    def test_parse_pid__no_such_block(self):
        self.assertRaises(Http404, parse_pid, 'b:1234.1')

    def test_parse_pid__location(self):
        loc = self._makeLocation()
        result = parse_pid('l:%d' % loc.id)
        self.assertEqual(result, (loc, None, None))

    def test_parse_pid__no_such_location(self):
        self.assertRaises(Http404, parse_pid, 'l:1234')

    def test_parse_pid__location_extra_args(self):
        loc = self._makeLocation()
        self.assertRaises(Http404, parse_pid, 'l:%d:1' % loc.id)

    def test_parse_pid__block__not_enough_args(self):
        b = self._makeBlock()
        self.assertRaises(Http404, parse_pid, 'b:%d' % b.id)

    def test_make_pid__block(self):
        b = self._makeBlock()
        self.assertEqual(make_pid(b, 1), 'b:%d.1' % b.id)

    def test_make_pid__block__default_radius(self):
        b = self._makeBlock()
        self.assertEqual(make_pid(b), 'b:%d.8' % b.id)

    def test_make_pid__location(self):
        loc = self._makeLocation()
        self.assertEqual(make_pid(loc), 'l:%d' % loc.id)

    def test_make_pid__wrong_type(self):
        self.assertRaises(ValueError, make_pid, object())

    def test_make_pid__location__extra_args(self):
        loc = self._makeLocation()
        self.assertRaises(AssertionError, make_pid, loc, '1')

    def test_make_and_parse_pid__block(self):
        block = self._makeBlock()
        self.assertEqual(parse_pid(make_pid(block, 1)),
                         (block, '1', BLOCK_RADIUS_CHOICES['1']))


    def test_make_and_parse_pid__location(self):
        loc = self._makeLocation()
        self.assertEqual(parse_pid(make_pid(loc)),
                         (loc, None, None))


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(PidTests)
    import doctest
    import ebpub.utils.text
    suite.addTest(doctest.DocTestSuite(ebpub.utils.text))
    import ebpub.utils.bunch
    suite.addTest(doctest.DocTestSuite(ebpub.utils.bunch))
    import ebpub.utils.dates
    suite.addTest(doctest.DocTestSuite(ebpub.utils.dates))
    import ebpub.utils.dates
    suite.addTest(doctest.DocTestSuite(ebpub.utils.geodjango))
    return suite

if __name__ == '__main__':
    unittest.main()


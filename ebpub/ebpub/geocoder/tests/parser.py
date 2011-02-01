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

from ebpub.geocoder.parser.parsing import strip_unit
import unittest

class StripUnitTestCase(unittest.TestCase):
    def assertStripUnit(self, text, expected):
        self.assertEqual(strip_unit(text), expected)

    def test_suite01(self):
        self.assertStripUnit('123 Main St Suite 1', '123 Main St')

    def test_suite02(self):
        self.assertStripUnit('123 Main St, Suite 1', '123 Main St')

    def test_suite03(self):
        self.assertStripUnit('123 Main St, Suite 2', '123 Main St')

    def test_suite04(self):
        self.assertStripUnit('123 Main St, Suite #2', '123 Main St')

    def test_suite05(self):
        self.assertStripUnit('123 Main St, Suite 465', '123 Main St')

    def test_suite06(self):
        self.assertStripUnit('123 Main St, Suite A', '123 Main St')

    def test_suite07(self):
        self.assertStripUnit('123 Main St, Suite AB', '123 Main St')

    def test_suite08(self):
        self.assertStripUnit('123 Main St, Suite 1A', '123 Main St')

    def test_suite09(self):
        self.assertStripUnit('123 Main St, Suite 2B', '123 Main St')

    def test_suite10(self):
        self.assertStripUnit('123 Main St, Suite 1-A', '123 Main St')

    def test_suite11(self):
        self.assertStripUnit('123 Main St, Suite #1', '123 Main St')

    def test_suite12(self):
        self.assertStripUnit('123 Main St, Suite #1A', '123 Main St')

    def test_suite13(self):
        self.assertStripUnit('123 Main St, Suite #1-A', '123 Main St')

    def test_suite14(self):
        self.assertStripUnit('123 Main St, Suite #A', '123 Main St')

    def test_ste1(self):
        self.assertStripUnit('123 Main St, Ste 14', '123 Main St')

    def test_ste2(self):
        self.assertStripUnit('123 Main St, Ste. 14', '123 Main St')

    def test_unit1(self):
        self.assertStripUnit('123 Main St, Unit 1W', '123 Main St')

    def test_hash1(self):
        self.assertStripUnit('123 Main St, #1', '123 Main St')

    def test_hash_dash(self):
        self.assertStripUnit('123 Main St, Ste K-#b', '123 Main St')

    def test_apt01(self):
        self.assertStripUnit('123 Main St, Apt 1', '123 Main St')

    def test_apt02(self):
        self.assertStripUnit('123 Main St, Apt. 1', '123 Main St')

    def test_space01(self):
        self.assertStripUnit('3015 Grand Avenue, Space 310', '3015 Grand Avenue')

    def test_unit_with_colon(self):
        self.assertStripUnit('325 Arlington Ave Unit: 140', '325 Arlington Ave')

if __name__ == "__main__":
    unittest.main()

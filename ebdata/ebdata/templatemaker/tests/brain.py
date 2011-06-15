#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

from ebdata.templatemaker.brain import Brain
from ebdata.templatemaker.hole import Hole, OrHole, IgnoreHole
import unittest

class BrainTestCase(unittest.TestCase):
    def assertAsText(self, brain, marker, expected):
        """
        Asserts that Brain(brain).as_text(marker) == expected.
        """
        b = Brain(brain)
        if marker is not None:
            self.assertEqual(b.as_text(marker), expected)
        else:
            self.assertEqual(b.as_text(), expected)

    def assertNumHoles(self, brain, expected):
        """
        Asserts that Brain(brain).num_holes() == expected.
        """
        b = Brain(brain)
        self.assertEqual(b.num_holes(), expected)

    def assertRegex(self, brain, expected):
        """
        Asserts that Brain(brain).match_regex() == expected.
        """
        b = Brain(brain)
        self.assertEqual(b.match_regex(), expected)

    def test_as_text_empty1(self):
        self.assertAsText([], None, '')

    def test_as_text_empty2(self):
        self.assertAsText([], 'marker', '')

    def test_as_text1(self):
        self.assertAsText(['1', Hole(), '2', Hole(), '3'], None, '1{{ HOLE }}2{{ HOLE }}3')

    def test_as_text2(self):
        self.assertAsText(['1', Hole(), '2', Hole(), '3'], '!', '1!2!3')

    def test_num_holes_empty(self):
        self.assertNumHoles([], 0)

    def test_num_holes1(self):
        self.assertNumHoles(['a', 'b', 'c'], 0)

    def test_num_holes2(self):
        self.assertNumHoles(['a', Hole(), 'c'], 1)

    def test_num_holes3(self):
        self.assertNumHoles(['a', Hole(), 'c', Hole()], 2)

    def test_regex_empty(self):
        self.assertRegex([], '^(?s)$')

    def test_regex_noholes(self):
        self.assertRegex(['a', 'b', 'c'], '^(?s)abc$')

    def test_regex_special_chars(self):
        self.assertRegex(['^$?.*'], r'^(?s)\^\$\?\.\*$')

    def test_regex_holes1(self):
        self.assertRegex(['a', Hole(), 'b'], '^(?s)a(.*?)b$')

    def test_regex_holes2(self):
        self.assertRegex(['a', OrHole('b', 'c'), 'd', IgnoreHole()], '^(?s)a(b|c)d.*?$')

class BrainEmptyTestCase(unittest.TestCase):
    def assertConcise(self, brain, expected):
        """
        Asserts that Brain(brain).concise() == expected.
        """
        b = Brain(brain)
        self.assertEqual(b.concise(), expected)

    def test_empty(self):
        self.assertConcise([], [])

    def test_basic1(self):
        self.assertConcise(['a'], ['a'])

    def test_basic2(self):
        self.assertConcise(['a', 'b'], ['ab'])

    def test_basic3(self):
        self.assertConcise(['a', Hole(), 'b'], ['a', Hole(), 'b'])

    def test_basic4(self):
        self.assertConcise([Hole(), 'a', Hole(), 'b'], [Hole(), 'a', Hole(), 'b'])

    def test_basic5(self):
        self.assertConcise([Hole(), 'a', Hole(), 'b', Hole()],
            [Hole(), 'a', Hole(), 'b', Hole()])

    def test_basic6(self):
        self.assertConcise([Hole(), 'a', 'b', 'c', Hole(), 'd', 'e', 'f', Hole(), 'g'],
            [Hole(), 'abc', Hole(), 'def', Hole(), 'g'])

    def test_long_strings(self):
        self.assertConcise(['this is ', 'a test', Hole(), 'of the ', 'emergency ', 'broadcast system', Hole()],
            ['this is a test', Hole(), 'of the emergency broadcast system', Hole()])

class BrainSerialization(unittest.TestCase):
    def assertSerializes(self, brain):
        """
        Serializes and unserializes the given brain, asserting that a round
        trip works properly.
        """
        b = Brain(brain)
        self.assertEqual(b, Brain.from_serialized(b.serialize()))

    def test_empty(self):
        self.assertSerializes([])

    def test_integer(self):
        self.assertSerializes([1, 2, 3])

    def test_string(self):
        self.assertSerializes(['abc', 'd', 'e', 'fg hi jklmnop'])

    def test_hole1(self):
        self.assertSerializes([Hole()])

    def test_hole2(self):
        self.assertSerializes([Hole(), Hole(), Hole()])

    def test_hole_and_strings(self):
        self.assertSerializes([Hole(), 'abc', Hole(), 'def', Hole()])

    def test_format1(self):
        self.assertEqual(Brain([]).serialize(), 'gAJjZWJkYXRhLnRlbXBsYXRlbWFrZXIuYnJhaW4KQnJhaW4KcQEpgXECfXEDYi4=\n')

    def test_format2(self):
        self.assertEqual(Brain([Hole(), 'abc', Hole()]).serialize(),
                         'gAJjZWJkYXRhLnRlbXBsYXRlbWFrZXIuYnJhaW4KQnJhaW4KcQEpgXECKGNlYmRhdGEudGVtcGxh\ndGVtYWtlci5ob2xlCkhvbGUKcQMpgXEEfXEFYlUDYWJjcQZoAymBcQd9cQhiZX1xCWIu\n'
                         )

    def test_format_input1(self):
        # If this fails due to eg. module renaming, you can recreate
        # correct output like: Brain([]).serialize()
        serialized = 'gAJjZWJkYXRhLnRlbXBsYXRlbWFrZXIuYnJhaW4KQnJhaW4KcQEpgXECfXEDYi4=\n'
        self.assertEqual(Brain([]), Brain.from_serialized(serialized))

    def test_format_input2(self):
        # If this fails due to eg. module renaming, you can recreate
        # correct output like: Brain([Hole(), 'abc', Hole()]).serialize()
        serialized = 'gAJjZWJkYXRhLnRlbXBsYXRlbWFrZXIuYnJhaW4KQnJhaW4KcQEpgXECKGNlYmRhdGEudGVtcGxh\ndGVtYWtlci5ob2xlCkhvbGUKcQMpgXEEfXEFYlUDYWJjcQZoAymBcQd9cQhiZX1xCWIu\n'
        self.assertEqual(Brain([Hole(), 'abc', Hole()]),
                         Brain.from_serialized(serialized))


if __name__ == "__main__":
    unittest.main()

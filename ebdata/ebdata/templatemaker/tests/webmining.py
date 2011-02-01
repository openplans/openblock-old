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

from ebdata.templatemaker.webmining import mine_page
import unittest

class MinePageTestCase(unittest.TestCase):
    def assertMines(self, html, others, expected):
        """
        Asserts that the given HTML strings will produce a tree_diff of the
        expected HTML string.
        """
        got = mine_page(html, others)
        self.assertEqual(got, expected)

    def test_basic(self):
        self.assertMines(
            '<h1>Bird flies</h1>',
            ['<h1>Man walks</h1>'],
            ['Bird flies']
        )

    def test_convert_newlines(self):
        self.assertMines(
            '<p>The person\nfell down the stairs.</p>',
            ['<p>Foo</p>'],
            ['<p>The person fell down the stairs.</p>']
        )

    def test_convert_tabs(self):
        self.assertMines(
            '<p>The person\tfell down the stairs.</p>',
            ['<p>Foo</p>'],
            ['<p>The person fell down the stairs.</p>']
        )

    def test_convert_nbsp1(self):
        self.assertMines(
            '<p>The person&nbsp;fell down the stairs.</p>',
            ['<p>Foo</p>'],
            ['<p>The person fell down the stairs.</p>']
        )

    def test_convert_nbsp2(self):
        self.assertMines(
            '<p>The person&#160;fell down the stairs.</p>',
            ['<p>Foo</p>'],
            ['<p>The person fell down the stairs.</p>']
        )

    def test_drop_nonalpha_lines1(self):
        self.assertMines(
            '<h1>-</h1>',
            ['<h1>??</h1>'],
            []
        )

    def test_drop_nonalpha_lines2(self):
        self.assertMines(
            '<h1>1</h1>',
            ['<h1>-</h1>'],
            ['1']
        )

    def test_drop_nonalpha_lines3(self):
        self.assertMines(
            '<h1><br>-</h1>',
            ['<h1><br>??</h1>'],
            []
        )

if __name__ == "__main__":
    unittest.main()

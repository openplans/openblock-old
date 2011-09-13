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

"""
Unit tests for ebdata/textmining/treeutils.py
"""

from ebdata.textmining.treeutils import make_tree, preprocess
from lxml import etree
import unittest

class MakeTreeTestCase(unittest.TestCase):
    def assertMakeTree(self, html, expected):
        import warnings
        # Note, warnings.catch_warnings() should work but has no effect here?
        warnings.simplefilter('ignore', UnicodeWarning)
        got = etree.tostring(make_tree(html), method='html')
        self.assertEqual(got, expected)

    def test_basic1(self):
        self.assertMakeTree('<html><body><h1>Hello</h1></body></html>', '<html><body><h1>Hello</h1></body></html>')

    def test_lxml_magic_behavior(self):
        # lxml sometimes reorders elements, depending on whether they're
        # block/inline.
        self.assertMakeTree('<html><body><h1><p><span>Hello</span></p></h1></body></html>',
            '<html><body><h1></h1><p><span>Hello</span></p></body></html>')

    def test_empty1(self):
        self.assertMakeTree('<html></html>', '<html></html>')

    def test_empty2(self):
        self.assertMakeTree('<html><body></body></html>', '<html><body></body></html>')

    def test_newlines(self):
        self.assertMakeTree('<html><body>\r\n\r\n\r\n</body></html>', '<html><body>\n\n\n</body></html>')

    def test_unicode_xml_declaration(self):
        self.assertMakeTree(u'<?xml version="1.0" encoding="utf-8"?><html><body><h1>Hello</h1></body></html>', '<html><body><h1>Hello</h1></body></html>')

class PreprocessTestCase(unittest.TestCase):
    def assertPreprocesses(self, html, expected, **kwargs):
        import warnings
        with warnings.catch_warnings():
            tree = make_tree(html)
            got = etree.tostring(preprocess(tree, **kwargs), method='html')
            self.assertEqual(got, expected)

    def test_comment1(self):
        self.assertPreprocesses('<html><body><!-- comment --></body></html>', '<html><body></body></html>')

    def test_comment2(self):
        self.assertPreprocesses('<html><body> <!--\n comment\n --> </body></html>', '<html><body>  </body></html>')

    def test_comment3(self):
        self.assertPreprocesses('<html><body> <!-- <p>Test</p> --> </body></html>', '<html><body>  </body></html>')

    def test_comment4(self):
        self.assertPreprocesses('<html><body> <!-- <p>Test</p> --> <!-- <p>Again</p> --> </body></html>', '<html><body>   </body></html>')

    def test_style1(self):
        self.assertPreprocesses('<html><head><style type="text/css">\n#foo { font: 11px verdana,sans-serif; }\n</style></head><body>Hi</body></html>', '<html><head></head><body>Hi</body></html>')

    def test_link1(self):
        self.assertPreprocesses('<html><head><link rel="stylesheet" src="/style.css"></head><body>Hi</body></html>', '<html><head></head><body>Hi</body></html>')

    def test_meta1(self):
        self.assertPreprocesses('<html><head><meta name="robots" content="noarchive"></head><body>Hi</body></html>', '<html><head></head><body>Hi</body></html>')

    def test_script1(self):
        self.assertPreprocesses('<html><head><script type="text/javascript">alert("hello");</script></head><body>Hi</body></html>', '<html><head></head><body>Hi</body></html>')

    def test_noscript1(self):
        self.assertPreprocesses('<html><body>Hi <noscript>You have no JavaScript</noscript> </body></html>', '<html><body>Hi  </body></html>')

    def test_droptags1(self):
        self.assertPreprocesses('<html><body><h1>Hello</h1></body></html>', '<html><body><h1>Hello</h1></body></html>')
        self.assertPreprocesses('<html><body><h1>Hello</h1></body></html>', '<html><body>Hello</body></html>', drop_tags=('h1',))

    def test_droptags2(self):
        self.assertPreprocesses('<html><body><div><p>Hello</p></div></body></html>', '<html><body><div><p>Hello</p></div></body></html>')
        self.assertPreprocesses('<html><body><div><p>Hello</p></div></body></html>', '<html><body><p>Hello</p></body></html>', drop_tags=('div',))
        self.assertPreprocesses('<html><body><div><p>Hello</p></div></body></html>', '<html><body><div>Hello</div></body></html>', drop_tags=('p',))

    def test_droptrees1(self):
        self.assertPreprocesses('<html><body><h1>Hello</h1></body></html>', '<html><body><h1>Hello</h1></body></html>')
        self.assertPreprocesses('<html><body><h1>Hello</h1></body></html>', '<html><body></body></html>', drop_trees=('h1',))

    def test_droptrees3(self):
        self.assertPreprocesses('<html><body><div><p>Hello</p></div></body></html>', '<html><body><div><p>Hello</p></div></body></html>')
        self.assertPreprocesses('<html><body><div><p>Hello</p></div></body></html>', '<html><body></body></html>', drop_trees=('div',))

    def test_droptrees4(self):
        self.assertPreprocesses('<html><body><div><p><span>Hello</span></p></div></body></html>', '<html><body><div><p><span>Hello</span></p></div></body></html>')
        self.assertPreprocesses('<html><body><div><p><span>Hello</span></p></div></body></html>', '<html><body></body></html>', drop_trees=('div',))

    def test_dropattrs(self):
        self.assertPreprocesses('<html><body><div id="foo" class="bar">Hi</div></body></html>', '<html><body><div id="foo" class="bar">Hi</div></body></html>')
        self.assertPreprocesses('<html><body><div id="foo" class="bar">Hi</div></body></html>', '<html><body><div class="bar">Hi</div></body></html>', drop_attrs=('id',))

    def test_drop_namespaced_attrs1(self):
        self.assertPreprocesses('<html><body><div dc:foo="foo">Hi</div></body></html>', '<html><body><div>Hi</div></body></html>')

    def test_drop_namespaced_attrs2(self):
        self.assertPreprocesses('<html><body><div dc:foo="foo" id="bar">Hi</div></body></html>', '<html><body><div id="bar">Hi</div></body></html>')

if __name__ == "__main__":
    unittest.main()

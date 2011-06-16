#   Copyright 2011 OpenPlans, and contributors
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

from django import template
from ebpub.db.templatetags import eb_filter
import mock
import unittest

class TestDoFilterUrl(unittest.TestCase):

    def setUp(self):
        self.mock_parser = mock.Mock()
        self.mock_token = mock.Mock()
        self.mock_filterchain = mock.Mock()
        # Monkeypatching because Variable has no useful equality test by default
        template.Variable.__eq__ = lambda self, other: self.var == other.var

    def tearDown(self):
        del(template.Variable.__eq__)

    def test__invalid_no_filterchain(self):
        self.mock_token.split_contents.return_value = ['filter_url']
        self.assertRaises(template.TemplateSyntaxError,
                          eb_filter.do_filter_url, self.mock_parser, self.mock_token)

    def test__invalid__bad_addition(self):
        self.mock_token.split_contents.return_value = ['filter_url', 'filterchain', 'oops']
        self.assertRaises(template.TemplateSyntaxError,
                          eb_filter.do_filter_url, self.mock_parser, self.mock_token)

    def test__invalid__bad_addition2(self):
        self.mock_token.split_contents.return_value = [
            'filter_url', 'filterchain', '+', 'oops']
        self.assertRaises(template.TemplateSyntaxError,
                          eb_filter.do_filter_url, self.mock_parser, self.mock_token)

    def test__invalid__bad_removal(self):
        self.mock_token.split_contents.return_value = [
            'filter_url', 'filterchain', '-', 'oops']

        self.assertRaises(template.TemplateSyntaxError,
                          eb_filter.do_filter_url, self.mock_parser, self.mock_token)

    def test__only_filterchain(self):
        self.mock_token.split_contents.return_value = ['filter_url',
                                                       'filterchain']
        node = eb_filter.do_filter_url(self.mock_parser, self.mock_token)
        self.assertEqual(node.additions, ())
        self.assertEqual(node.removals, ())
        self.assertEqual(node.filterchain_var.var, 'filterchain')

    def test__addition_no_args(self):
        self.mock_token.split_contents.return_value = [
            'filter_url', 'filterchain', '+maybe']
        node = eb_filter.do_filter_url(self.mock_parser, self.mock_token)
        self.assertEqual(node.additions, ((template.Variable('maybe'), ()),))

    def test__additions(self):
        self.mock_token.split_contents.return_value = ['filter_url',
                                                       'filterchain',
                                                       '+foo', 'foo2',
                                                       '+bar', 'bar2', 'bar3',
                                                       '+baz', 'baz2']
        node = eb_filter.do_filter_url(self.mock_parser, self.mock_token)
        self.assertEqual(node.removals, ())
        self.assertEqual(len(node.additions), 3)
        from django.template import Variable
        expected = ((Variable('foo'), (Variable('foo2'),)),
                    (Variable('bar'), (Variable('bar2'), Variable('bar3'))),
                    (Variable('baz'), (Variable('baz2'),)))

        self.assertEqual(node.additions, expected)

    def test__removals(self):
        self.mock_token.split_contents.return_value = ['filter_url',
                                                       'filterchain',
                                                       '-foo', '-bar', '-baz']
        node = eb_filter.do_filter_url(self.mock_parser, self.mock_token)
        self.assertEqual(node.additions, ())
        self.assertEqual(len(node.removals), 3)
        Variable = template.Variable
        expected = (Variable('foo'), Variable('bar'), Variable('baz'))
        self.assertEqual(node.removals, expected)

    def test__additions_and_removals(self):
        self.mock_token.split_contents.return_value = ['filter_url',
                                                       'filterchain',
                                                       '-foo',
                                                       '+bar', 'bar2',
                                                       '-baz']
        node = eb_filter.do_filter_url(self.mock_parser, self.mock_token)
        self.assertEqual(len(node.removals), 2)
        self.assertEqual(len(node.additions), 1)

        Variable = template.Variable
        self.assertEqual(node.additions,
                         ((Variable('bar'), (Variable('bar2'),)),))
        self.assertEqual(node.removals,
                         (Variable('foo'), Variable('baz')))

    def test_render(self):
        from ebpub.db.schemafilters import FilterChain
        mock_chain = mock.Mock(spec=FilterChain)
        # Hack so mock_chain() also inherits FilterChain
        mock_chain.return_value = mock_chain
        mock_chain.schema = mock.Mock()
        mock_chain.make_url.return_value = 'ok'
        mock_chain.schema.url.return_value = 'http://X/'

        context = {'filterchain': mock_chain,
                   'add1': 'X', 'add2': 'Y', 'remove1': 'Z'}
        node = eb_filter.FilterUrlNode('filterchain',
                                       [('add1', ('add2',))],
                                       ['remove1'])
        self.assertEqual(node.render(context), 'ok')
        self.assertEqual(mock_chain.make_url.call_args,
                         ((), {'additions': [('X', ['Y'])], 'removals': ['Z']}))

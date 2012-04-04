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

from django.core import urlresolvers
from django import template
from django.template import base as template_base
from django.template import loader
from django.utils.translation import activate, deactivate
from ebpub.db.templatetags import eb_filter
from ebpub.db.templatetags import eb
from ebpub.utils.django_testcase_backports import TestCase
import mock
import os
import sys
import traceback
import unittest

class TestFilterUrl(unittest.TestCase):

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
                          eb_filter.filter_url, self.mock_parser, self.mock_token)

    def test__invalid__bad_addition(self):
        self.mock_token.split_contents.return_value = ['filter_url', 'filterchain', 'oops']
        self.assertRaises(template.TemplateSyntaxError,
                          eb_filter.filter_url, self.mock_parser, self.mock_token)

    def test__invalid__bad_addition2(self):
        self.mock_token.split_contents.return_value = [
            'filter_url', 'filterchain', '+', 'oops']
        self.assertRaises(template.TemplateSyntaxError,
                          eb_filter.filter_url, self.mock_parser, self.mock_token)

    def test__invalid__bad_removal(self):
        self.mock_token.split_contents.return_value = [
            'filter_url', 'filterchain', '-', 'oops']

        self.assertRaises(template.TemplateSyntaxError,
                          eb_filter.filter_url, self.mock_parser, self.mock_token)

    def test__only_filterchain(self):
        self.mock_token.split_contents.return_value = ['filter_url',
                                                       'filterchain']
        node = eb_filter.filter_url(self.mock_parser, self.mock_token)
        self.assertEqual(node.additions, ())
        self.assertEqual(node.removals, ())
        self.assertEqual(node.filterchain_var.var, 'filterchain')

    def test__addition_no_args(self):
        self.mock_token.split_contents.return_value = [
            'filter_url', 'filterchain', '+maybe']
        node = eb_filter.filter_url(self.mock_parser, self.mock_token)
        self.assertEqual(node.additions, ((template.Variable('maybe'), ()),))

    def test__additions(self):
        self.mock_token.split_contents.return_value = ['filter_url',
                                                       'filterchain',
                                                       '+foo', 'foo2',
                                                       '+bar', 'bar2', 'bar3',
                                                       '+baz', 'baz2']
        node = eb_filter.filter_url(self.mock_parser, self.mock_token)
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
        node = eb_filter.filter_url(self.mock_parser, self.mock_token)
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
        node = eb_filter.filter_url(self.mock_parser, self.mock_token)
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


class TestSimpleTags(unittest.TestCase):
    # Misc tags that don't require a database for testing.

    def test_schema_plural_name(self):
        class stubschema:
            name = 'dog'
            plural_name = 'dogs'

        self.assertEqual(eb.schema_plural_name(stubschema, 0), 'dogs')
        self.assertEqual(eb.schema_plural_name(stubschema, 1), 'dog')
        self.assertEqual(eb.schema_plural_name(stubschema, 2), 'dogs')
        self.assertEqual(eb.schema_plural_name(stubschema, -1), 'dogs')
        self.assertEqual(eb.schema_plural_name(stubschema, 999), 'dogs')

    def test_schema_plural_name__list(self):
        class stubschema:
            name = 'dog'
            plural_name = 'dogs'

        self.assertEqual(eb.schema_plural_name(stubschema, []), 'dogs')
        self.assertEqual(eb.schema_plural_name(stubschema, [None]), 'dog')
        self.assertEqual(eb.schema_plural_name(stubschema, [None, None]), 'dogs')

    def test_safe_id_sort(self):
        class Item(dict):
            def __init__(self, id, *args, **kwargs):
                self.id = id
                self.update(kwargs)

        items = [
            Item(3, a=1, b=2, c=3),
            Item(4, a=1, b=2, c=3),
            Item(-1, a=1, b=2, c=3),
            Item(4, a=1, b=-999, c=3),
            ]
        result = eb.safe_id_sort(items, 'b')
        self.assertEqual([(item['b'], item.id) for item in result],
                         [(-999, 4),
                          (2, -1),
                          (2, 3),
                          (2, 4)]
                         )


    def test_get_metro(self):
        import ebpub.metros.allmetros
        context = {}
        eb.get_metro(context)
        self.assertEqual(context['METRO'], ebpub.metros.allmetros.get_metro())

    def test_get_metro_list(self):
        import ebpub.metros.allmetros
        context = {}
        eb.get_metro_list(context)
        self.assertEqual(context['METRO_LIST'], ebpub.metros.allmetros.METRO_LIST)


from django.conf import settings

class ShouldNotExecuteException(Exception):
    pass

class ContextStackException(Exception):
    pass


class BaseTemplateTagSetup(object):

    # The actual test cases are a dictionary returned by self.get_template_tests().

    # Partially copied from django.tests.regressiontests.templates.tests,
    # which is not available for import if we don't have a development checkout
    # of Django.

    def setUp(self):
        from django.test.utils import get_warnings_state
        import warnings
        self._warnings_state = get_warnings_state()
        warnings.filterwarnings('ignore', category=DeprecationWarning,
                                module='django.template.defaulttags')

        self.old_static_url = settings.STATIC_URL
        self.old_media_url = settings.MEDIA_URL
        settings.STATIC_URL = u"/static/"

        settings.MEDIA_URL = u"/media/"

    def tearDown(self):
        from django.test.utils import restore_warnings_state
        settings.STATIC_URL = self.old_static_url
        settings.MEDIA_URL = self.old_media_url
        restore_warnings_state(self._warnings_state)

    def test_templates(self):
        from django.test.utils import setup_test_template_loader
        from django.test.utils import restore_template_loaders

        template_tests = self.get_template_tests()
        filter_tests = {}  #filters.get_filter_tests()

        # Quickly check that we aren't accidentally using a name in both
        # template and filter tests.
        overlapping_names = [name for name in filter_tests if name in template_tests]
        assert not overlapping_names, 'Duplicate test name(s): %s' % ', '.join(overlapping_names)

        template_tests.update(filter_tests)

        cache_loader = setup_test_template_loader(
            dict([(name, t[0]) for name, t in template_tests.iteritems()]),
            use_cached_loader=True,
        )
        failures = []

        # Turn TEMPLATE_DEBUG off, because tests assume that.
        old_td, settings.TEMPLATE_DEBUG = settings.TEMPLATE_DEBUG, False

        # Set TEMPLATE_STRING_IF_INVALID to a known string.
        old_invalid = settings.TEMPLATE_STRING_IF_INVALID
        expected_invalid_str = 'INVALID'

        #Set ALLOWED_INCLUDE_ROOTS so that ssi works.
        old_allowed_include_roots = settings.ALLOWED_INCLUDE_ROOTS
        settings.ALLOWED_INCLUDE_ROOTS = (
            os.path.dirname(os.path.abspath(__file__)),
            )

        try:
            # Openblock: Original code copied from django regression tests
            # didn't have a try/finally block here, which meant any failure
            # below would cause failure to restore template loaders etc.,
            # with disastrous effects for other test suites.
            tests = template_tests.items()
            tests.sort()
            # Warm the URL reversing cache. This ensures we don't pay the cost
            # warming the cache during one of the tests.
            urlresolvers.reverse('ebpub-homepage')

            for name, vals in tests:
                if isinstance(vals[2], tuple):
                    normal_string_result = vals[2][0]
                    invalid_string_result = vals[2][1]

                    if isinstance(invalid_string_result, tuple):
                        expected_invalid_str = 'INVALID %s'
                        invalid_string_result = invalid_string_result[0] % invalid_string_result[1]
                        template_base.invalid_var_format_string = True

                    try:
                        template_debug_result = vals[2][2]
                    except IndexError:
                        template_debug_result = normal_string_result

                else:
                    normal_string_result = vals[2]
                    invalid_string_result = vals[2]
                    template_debug_result = vals[2]

                if 'LANGUAGE_CODE' in vals[1]:
                    activate(vals[1]['LANGUAGE_CODE'])
                else:
                    activate('en-us')
                for invalid_str, template_debug, result in [
                        ('', False, normal_string_result),
                        (expected_invalid_str, False, invalid_string_result),
                        ('', True, template_debug_result)
                    ]:
                    settings.TEMPLATE_STRING_IF_INVALID = invalid_str
                    settings.TEMPLATE_DEBUG = template_debug
                    for is_cached in (False, True):
                        try:
                            try:
                                test_template = loader.get_template(name)
                            except ShouldNotExecuteException:
                                failures.append("Template test (Cached='%s', TEMPLATE_STRING_IF_INVALID='%s', TEMPLATE_DEBUG=%s): %s -- FAILED. Template loading invoked method that shouldn't have been invoked." % (is_cached, invalid_str, template_debug, name))

                            try:
                                output = self.render(test_template, vals)
                            except ShouldNotExecuteException:
                                failures.append("Template test (Cached='%s', TEMPLATE_STRING_IF_INVALID='%s', TEMPLATE_DEBUG=%s): %s -- FAILED. Template rendering invoked method that shouldn't have been invoked." % (is_cached, invalid_str, template_debug, name))
                        except ContextStackException:
                            failures.append("Template test (Cached='%s', TEMPLATE_STRING_IF_INVALID='%s', TEMPLATE_DEBUG=%s): %s -- FAILED. Context stack was left imbalanced" % (is_cached, invalid_str, template_debug, name))
                            continue
                        except Exception:
                            exc_type, exc_value, exc_tb = sys.exc_info()
                            if exc_type != result:
                                tb = '\n'.join(traceback.format_exception(exc_type, exc_value, exc_tb))
                                failures.append("Template test (Cached='%s', TEMPLATE_STRING_IF_INVALID='%s', TEMPLATE_DEBUG=%s): %s -- FAILED. Got %s, exception: %s\n%s" % (is_cached, invalid_str, template_debug, name, exc_type, exc_value, tb))
                            continue
                        if output != result:
                            failures.append("Template test (Cached='%s', TEMPLATE_STRING_IF_INVALID='%s', TEMPLATE_DEBUG=%s): %s -- FAILED. Expected %r, got %r" % (is_cached, invalid_str, template_debug, name, result, output))
                    cache_loader.reset()

                if 'LANGUAGE_CODE' in vals[1]:
                    deactivate()

                if template_base.invalid_var_format_string:
                    expected_invalid_str = 'INVALID'
                    template_base.invalid_var_format_string = False
        finally:
            restore_template_loaders()
            deactivate()
            settings.TEMPLATE_DEBUG = old_td
            settings.TEMPLATE_STRING_IF_INVALID = old_invalid
            settings.ALLOWED_INCLUDE_ROOTS = old_allowed_include_roots

        self.assertEqual(failures, [], "Tests failed:\n%s\n%s" %
            ('-'*70, ("\n%s\n" % ('-'*70)).join(failures)))

    def render(self, test_template, vals):
        context = template.Context(vals[1])
        before_stack_size = len(context.dicts)
        output = test_template.render(context)
        if len(context.dicts) != before_stack_size:
            raise ContextStackException
        return output


class TemplateTagTests(BaseTemplateTagSetup, unittest.TestCase):

    def setUp(self):
        self.patchers = {
            'get_metro': mock.patch('ebpub.metros.allmetros.get_metro'),
            }
        self.mock_get_metro = self.patchers['get_metro'].start()
        self.mock_get_metro.return_value = {'metro_name': 'Test Metro',
                                            'city_name': 'Test City',
                                            'short_name': 'test',
                                            'state': 'XY',
                                            'multiple_cities': False,
                                            }

    def tearDown(self):
        for patcher in self.patchers.values():
            patcher.stop()


    def get_template_tests(self):
        # SYNTAX --
        # 'template_name': ('template contents', 'context dict', 'expected string output' or Exception class)
        #basedir = os.path.dirname(os.path.abspath(__file__))
        from django import template
        tests = {
            #'cycle01': ('{% cycle a %}', {}, template.TemplateSyntaxError),
            'METRO_NAME': ('{% load eb %}{% METRO_NAME %}', {}, self.mock_get_metro()['metro_name']),
            }
        return tests



class TestTemplateTagsWithDatabase(BaseTemplateTagSetup, TestCase):

    fixtures = ('test-schemafilter-views.json',)

    def get_template_tests(self):
        # SYNTAX --
        # 'template_name': ('template contents', 'context dict', 'expected string output' or Exception class)
        #basedir = os.path.dirname(os.path.abspath(__file__))
        from ebpub.db.models import NewsItem
        return {

            'get_newsitem1':
                ('{% load eb %}{% get_newsitem "1" as my_item %}{{my_item.title}}',
                 {}, 'crime title 1'),

            'get_newsitem2':
                ('{% load eb %}{% get_newsitem some_id as my_item %}{{my_item.title}}',
                 {'some_id': 1}, 'crime title 1'),

            'get_newsitem3':
                ('{% load eb %}{% get_newsitem "987654331" as my_item %}{{my_item.title}}',
                 {}, ('', 'INVALID')),

            'get_newsitem4':
                ('{% load eb %}{% get_newsitem %}', {}, template.TemplateSyntaxError),


            'get_newsitem_list_by_attr__error':
                ('{% load eb %}{% get_newsitem_list_by_attribute "crime" %}',
                 {}, template.TemplateSyntaxError),

            'get_newsitem_list_by_attr__slug':
                ('{% load eb %}{% get_newsitem_list_by_attribute "crime" type_id=58 as items %}{% for item in items %}{{ item.title }}. {% endfor %}',
                 {},
                 u'crime title 2. '),

            'get_newsitem_list_by_attr__schema':
                ('{% load eb %}{% get_newsitem_list_by_attribute myschema type_id=58 as items %}{% for item in items %}{{ item.title }}. {% endfor %}',
                 {'myschema': 1},
                 u'crime title 2. ',
                 ),


            'json_lookup_values_for_attribute':
                ('{% load eb %}{% json_lookup_values_for_attribute "crime" "tag" %}',
                 {},
                 u'["Tag 1", "Tag 2", "Tag 3", "Tag 999 UNUSED"]',
                 ),

            'get_locations_for_item__dict':
                ('{% load eb %}{% get_locations_for_item item neighborhoods as locs %}{% for loc in locs %}{{ loc.location_slug }}, {% endfor %}',
                 {'item': {'_item': NewsItem.objects.get(id=1)},},
                 u'hood-1, ',
                 ),

            'get_locations_for_item__newsitem':
                ('{% load eb %}{% get_locations_for_item item neighborhoods nonexistent-loctype-slug as locs %}{% for loc in locs %}{{ loc.location_slug }}, {% endfor %}',
                 {'item': NewsItem.objects.get(id=1),},
                 u'hood-1, ',
                 ),


            'get_locations_for_item__not_enough_args':
                ('{% load eb %}{% get_locations_for_item item as locs %}{% for loc in locs %}{{ loc.location_slug }}, {% endfor %}',
                 {'item': {'_item': NewsItem.objects.get(id=2)}},
                 template.TemplateSyntaxError,
                 ),

            'get_locations_for_item__bad_args':
                ('{% load eb %}{% get_locations_for_item item OUCHIE locs %}{% for loc in locs %}{{ loc.location_slug }}, {% endfor %}',
                 {'item': {'_item': NewsItem.objects.get(id=2)}},
                 template.TemplateSyntaxError,
                 ),

            'get_locations_for_item__not_item':
                ('{% load eb %}{% get_locations_for_item item neighborhoods as locs %}{% for loc in locs %}{{ loc.location_slug }}, {% endfor %}',
                 {'item': 'whoops'}, template.TemplateSyntaxError,
                 ),

            }

#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings

from django.test.simple import DjangoTestSuiteRunner, TestCase
from django.test.simple import reorder_suite, build_test, build_suite
from django.db.models import get_app, get_apps
import unittest

class TestSuiteRunner(DjangoTestSuiteRunner):
    """
    This is a custom test runner for OpenBlock.
    """
    
#    def setup_databases(self, **kwargs):
#    def teardown_databases(self, old_config, **kwargs):

    # If you use Nose, you don't want it to think this class & its
    # methods are tests:
    __test__ = False

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = unittest.TestSuite()
        if test_labels:
            for label in test_labels:
                if '.' in label:
                    suite.addTest(build_test(label))
                else:
                    app = get_app(label)
                    suite.addTest(build_suite(app))
        else:
            print "Excluding apps: %s" % ', '.join(settings.APPS_NOT_FOR_TESTING)
            for app in get_apps():
                if app.__package__ in settings.APPS_NOT_FOR_TESTING or \
                        app.__name__ in settings.APPS_NOT_FOR_TESTING:
                    continue
                print "Will test %s" % app.__name__
                suite.addTest(build_suite(app))

        if extra_tests:
            for test in extra_tests:
                print "Adding extra test %s" % test
                suite.addTest(test)

        return reorder_suite(suite, (TestCase,))

# Don't let Nose think this is a test case either:
build_test.__test__ = False

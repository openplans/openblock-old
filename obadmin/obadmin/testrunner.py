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

    EXCLUDED_APPS = [
        # the user model used is custom, these tests to not apply
        'django.contrib.auth.models',
        # this makes too many wierd assumptions about the database underpinnings
        'django.contrib.contenttypes.models'       
    ]

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
            for app in get_apps():
                if app.__name__ not in self.EXCLUDED_APPS:
                    print app.__name__
                    suite.addTest(build_suite(app))

        if extra_tests:
            for test in extra_tests:
                suite.addTest(test)

        return reorder_suite(suite, (TestCase,))
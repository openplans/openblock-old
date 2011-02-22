"""
API tests
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

class TestAPI(TestCase):

    def test_api_available(self):
        self.client.get(reverse('check_api_available'), status=200)
    

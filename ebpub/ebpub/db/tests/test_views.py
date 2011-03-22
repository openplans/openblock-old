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

"""
Unit tests for db.views.
"""

from django.core import urlresolvers
from django.test import TestCase

class ViewTestCase(TestCase):
    "Unit tests for views.py."
    fixtures = ('crimes',)

    def test_search__bad_schema(self):
        url = urlresolvers.reverse('ebpub.db.views.search', args=['kaboom'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_search__no_query(self):
        url = urlresolvers.reverse('ebpub.db.views.search', args=['crime'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], 'http://testserver/crime/')
        response = self.client.get(url + '?type=alert')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], 'http://testserver/crime/')

    def test_search(self):
        url = urlresolvers.reverse('ebpub.db.views.search', args=['crime'])
        response = self.client.get(url + '?q=228 S. Wabash Ave.')
        self.assertEqual(response.status_code, 200)
        assert 'location not found' in response.content.lower()
        # TODO: load a fixture with some locations and some news?


    def test_newsitem_detail(self):
        # response = self.client.get('')
        pass

    def test_location_redirect(self):
        # redirect to neighborhoods by default
        response = self.client.get('/locations/')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'http://testserver/locations/neighborhoods/')

    def test_location_type_detail(self):
        # response = self.client.get('')
        pass

    def test_location_detail(self):
        # response = self.client.get('')
        pass

    def test_schema_detail(self):
        response = self.client.get('/crime/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/nonexistent/')
        self.assertEqual(response.status_code, 404)

    def test_schema_xy_detail(self):
        # response = self.client.get('')
        pass

def filter_reverse(slug, args):
    for i, a  in enumerate(args):
        if isinstance(a, tuple):
            args[i] = a = list(a)
        if not isinstance(a[1], basestring):
            a[1] = ','.join(a[1])
    argstring = ';'.join(['%s=%s' % (k, v) for (k, v) in args])
    url = urlresolvers.reverse('ebpub-schema-filter', args=[slug, 'filter'])
    url = '%s%s/' % (url, argstring)
    return url

class TestSchemaFilterView(TestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json', 'crimes.json',)


    def test_filter_no_args(self):
        url = filter_reverse('crime', [])
        response = self.client.get(url)
        self.assertContains(response, 'choose a location')
        self.assertContains(response, 'id="date-filtergroup"')

    def test_filter_location_choices(self):
        url = filter_reverse('crime', [('locations', 'zipcodes')])
        response = self.client.get(url)
        self.assertContains(response, 'Select ZIP Code')
        self.assertContains(response, 'Zip 1')
        self.assertContains(response, 'Zip 2')

    def test_filter_location_detail(self):
        url = filter_reverse('crime', [('locations', ('zipcodes', 'zip-1'))])
        response = self.client.get(url)
        self.assertContains(response, 'Zip 1')
        self.assertNotContains(response, 'Zip 2')
        self.assertContains(response, 'Remove this filter')


    def test_filter_detail_month(self):
        url = filter_reverse('crime', [('by-date', ('2006-11-01', '2006-11-30'))])
        response = self.client.get(url)
        self.assertContains(response, 'Clear')
        self.assertNotContains(response, "HM609859")
        self.assertContains(response, "HM694545")
        self.assertContains(response, "HM696584")


    def test_filter_detail_day(self):
        # response = self.client.get('')
        pass

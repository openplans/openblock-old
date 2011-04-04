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

# Once we are on django 1.3, this becomes "from django.test.client import RequestFactory"
from .client import RequestFactory

import mock


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
    # Generate a reverse schema_filter URL.
    # XXX This should probably turn into something real,
    # not just a test helper.
    for i, a  in enumerate(args):
        if isinstance(a, tuple) or isinstance(a, list):
            # The first item is the arg name, the rest are arg values.
            if len(a) > 1:
                name = a[0]
                values = ','.join(a[1:])
                args[i] = '%s=%s' % (name, values)
            else:
                raise ValueError("param %s has no values" % a[0])
        else:
            assert isinstance(a, basestring)
    argstring = ';'.join(args) #['%s=%s' % (k, v) for (k, v) in args])
    url = urlresolvers.reverse('ebpub-schema-filter', args=[slug, 'filter'])
    url = '%s%s/' % (url, argstring)
    return url

class TestSchemaFilterView(TestCase):

    fixtures = ('test-locationtypes.json', 'test-locations.json', 'crimes.json',
                'wabash.yaml',
                )

    def test_filter_by_no_args(self):
        url = filter_reverse('crime', [])
        response = self.client.get(url)
        self.assertContains(response, 'choose a location')
        self.assertContains(response, 'id="date-filtergroup"')

    def test_filter_by_location_choices(self):
        url = filter_reverse('crime', [('locations', 'zipcodes')])
        response = self.client.get(url)
        self.assertContains(response, 'Select ZIP Code')
        self.assertContains(response, 'Zip 1')
        self.assertContains(response, 'Zip 2')

    def test_filter_by_location_detail(self):
        url = filter_reverse('crime', [('locations', 'zipcodes', 'zip-1')])
        response = self.client.get(url)
        self.assertContains(response, 'Zip 1')
        self.assertNotContains(response, 'Zip 2')
        self.assertContains(response, 'Remove this filter')


    def test_filter_by_daterange(self):
        url = filter_reverse('crime', [('by-date', '2006-11-01', '2006-11-30')])
        response = self.client.get(url)
        self.assertContains(response, 'Clear')
        self.assertNotContains(response, "crime title 1")
        self.assertContains(response, "crime title 2")
        self.assertContains(response, "crime title 3")

    def test_filter__only_one_date_allowed(self):
        url = filter_reverse('crime',
                             [('by-date', '2006-11-01', '2006-11-30'),
                              ('by-pub-date', '2006-11-01', '2006-11-30')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)


    def test_filter__invalid_daterange(self):
        url = filter_reverse('crime', [('by-date', '')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        url = filter_reverse('crime', [('by-date', 'whoops', 'ouchie')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        url = filter_reverse('crime', [('by-date', '2006-11-30', 'ouchie')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)


    def test_filter_by_day(self):
        url = filter_reverse('crime', [('by-date', '2006-09-26', '2006-09-26')])
        response = self.client.get(url)
        self.assertContains(response, "crime title 1")
        self.assertNotContains(response, "crime title 2")
        self.assertNotContains(response, "crime title 3")


    def test_filter_by_attributes(self):
        url = filter_reverse('crime', [('by-status', 'status 9-19')])
        response = self.client.get(url)
        self.assertEqual(len(response.context['newsitem_list']), 1)
        self.assertContains(response, "crime title 1")
        self.assertNotContains(response, "crime title 2")
        self.assertNotContains(response, "crime title 3")

    def test_filter_by_attributes__bad_attr(self):
        url = filter_reverse('crime', [('by-bogosity', 'anything')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_attributes__bad_value(self):
        url = filter_reverse('crime', [('by-status', 'bogus')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "crime title ")

    def test_filter_by_street__missing_street(self):
        url = filter_reverse('crime', [('streets', '')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_street__missing_block(self):
        url = filter_reverse('crime', [('streets', 'wabash-ave',)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_street__bad_block(self):
        url = filter_reverse('crime', [('streets', 'bogus',)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_block__no_radius(self):
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        fixed_url = filter_reverse('crime', [
                ('streets', 'wabash-ave', '216-299n', '8-blocks')])
        self.assert_(response['location'].endswith(fixed_url))

    def test_filter_by_block(self):
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n', '8-blocks')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_filter__only_one_location_allowed(self):
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n', '8'),
                                       ('locations', 'zipcodes', 'zip-1'),
                                       ])
        response = self.client.get(url)
        url = filter_reverse('crime', [('locations', 'zipcodes', 'zip-1'),
                                       ('streets', 'wabash-ave', '216-299n', '8')
                                       ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_filter__by_location__unknown(self):
        url = filter_reverse('crime', [('locations', 'anything')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter__by_location__empty_location(self):
        url = filter_reverse('crime', [('locations', '')])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter_by_location(self):
        url = filter_reverse('crime', [('locations', 'zipcodes', 'zip-1'),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Zip 1')

    def test_filter__by_bad_lookup_attr(self):
        url = filter_reverse('crime', [('by-fleezleglop', '214', ),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filter__by_lookup_attr(self):
        url = filter_reverse('crime', [('by-beat', 'beat-214', ),])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Police Beat 214')

    def test_filter__by_m2m_lookup_attr(self):
        # XXX todo.
        # I don't think there are any m2m lookups in crimes.json yet
        pass

    def test_filter__by_boolean_attr(self):
        # XXX todo
        pass

    def test_normalize_filter_url__ok(self):
        from ebpub.db.views import _schema_filter_normalize_url
        url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n', '8'),])
        request = RequestFactory().get(url)
        self.assertEqual(None, _schema_filter_normalize_url(request))


    def test_normalize_filter_url__intersection(self):
        # XXX todo
        pass

    def test_normalize_filter_url__bad_address(self):
        from ebpub.db.views import _schema_filter_normalize_url
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter'])
        url += '?address=123+nowhere+at+all&radius=8'

        request = RequestFactory().get(url)
        from ebpub.db.views import BadAddressException
        self.assertRaises(BadAddressException,
                          _schema_filter_normalize_url, request)

    @mock.patch('ebpub.db.views.SmartGeocoder.geocode')
    def test_normalize_filter_url__redirect_querystring(self, mock_geocode):
        from ebpub.streets.models import Block
        block = Block.objects.get(street_slug='wabash-ave', from_num=216)
        mock_geocode.return_value = {
            'city': block.left_city.title(),
            'zip': block.left_zip,
            'point': block.geom.centroid,
            'state': block.left_state,
            'intersection_id': None,
            'address': u'216 N Wabash Ave',
            'intersection': None,
            'block': block,
            }
        from ebpub.db.views import _schema_filter_normalize_url
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter'])
        url += '?address=216+n+wabash+st&radius=8'

        expected_url = filter_reverse('crime', [('streets', 'wabash-ave', '216-299n', '8'),])
        request = RequestFactory().get(url)
        normalized_url = _schema_filter_normalize_url(request)
        self.assertEqual(expected_url, normalized_url)

    def test_normalize_filter_url__bad_dates(self):
        url = urlresolvers.reverse('ebpub-schema-filter', args=['crime', 'filter'])
        response = self.client.get(url + '?start_date=12/31/1899&end_date=01/01/2011')
        self.assertEqual(response.status_code, 400)

        response = self.client.get(url + '?start_date=01/01/2011&end_date=12/31/1899')
        self.assertEqual(response.status_code, 400)

        response = self.client.get(url + '?start_date=Whoops&end_date=Bzorch')
        self.assertEqual(response.status_code, 400)

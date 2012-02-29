#   Copyright 2011 OpenPlans and contributors
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
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.core import urlresolvers
from django.test import TestCase
from ebpub.openblockapi.tests import _make_items
from ebpub.db.models import NewsItem
from ebpub.db.models import Schema
import mock
import json


class TestViews(TestCase):

    def tearDown(self):
        NewsItem.objects.all().delete()
        Schema.objects.all().delete()


    @mock.patch('ebpub.richmaps.views.build_item_query')
    def test_map_items__no_params_no_items(self, mock_build_item_query):
        url = urlresolvers.reverse('map_items_json')
        mock_build_item_query.return_value = ([], {})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        decoded = json.loads(response.content)
        self.assertEqual(decoded,
                         {u'type': u'FeatureCollection',
                          u'features': []})

    @mock.patch('ebpub.richmaps.views.build_item_query')
    def test_map_items__no_params__with_items(self, mock_build_item_query):
        schema = Schema.objects.create(
            name='n1', plural_name='n1s',
            indefinite_article='a', last_updated='2012-01-01',
            date_name='dn', date_name_plural='dns')
        items = _make_items(3, schema)
        mock_build_item_query.return_value = (items, {})
        for item in items:
            item.save()
        url = urlresolvers.reverse('map_items_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        decoded = json.loads(response.content)
        self.assertEqual(len(decoded['features']), 3)


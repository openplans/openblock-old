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
Unit tests for db.models.
"""

from ebpub.utils.django_testcase_backports import TestCase
from ebpub.db.models import NewsItem, Attribute
import datetime

class DatabaseExtensionsTestCase(TestCase):
    "Unit tests for the custom ORM stuff in models.py."
    fixtures = ('crimes.json',)

    def testAttributesLazilyLoaded(self):
        # Attributes are retrieved lazily the first time you access the
        # `attributes` attribute.

        # Turn DEBUG on and reset queries, so we can keep track of queries.
        # This is hackish.
        from django.db import connection
        connection.queries = []
        with self.settings(DEBUG=True):
            ni = NewsItem.objects.get(id=1)
            self.assertEquals(ni.attributes['case_number'], u'case number 1')
            self.assertEquals(ni.attributes['crime_date'], datetime.date(2006, 9, 19))
            self.assertEquals(ni.attributes['crime_time'], None)
            self.assertEquals(len(connection.queries), 3)
            connection.queries = []

    def testSetAllAttributesNonDict(self):
        # Setting `attributes` to something other than a dictionary will raise
        # ValueError.
        ni = NewsItem.objects.get(id=1)
        def setAttributeToNonDict():
            ni.attributes = 1
        self.assertRaises(ValueError, setAttributeToNonDict)

    def testSetAllAttributes1(self):
        # Attributes can be set by assigning a dictionary to the `attributes`
        # attribute. As soon as `attributes` is assigned-to, the UPDATE query
        # is executed in the database.
        ni = NewsItem.objects.get(id=1)
        self.assertEquals(ni.attributes['case_number'], u'case number 1')
        ni.attributes = dict(ni.attributes, case_number=u'Hello')
        self.assertEquals(Attribute.objects.get(news_item__id=1).varchar01, u'Hello')

    def testSetAllAttributes2(self):
        # Setting attributes works even if you don't access them first.
        ni = NewsItem.objects.get(id=1)
        ni.attributes = {
            u'arrests': False,
            u'beat': 214,
            u'block_id': 25916,
            u'case_number': u'Hello',
            u'crime_date': datetime.date(2006, 9, 19),
            u'crime_time': None,
            u'domestic': False,
            u'is_outdated': True,
            u'location_id': 66,
            u'police_id': None,
            u'status': u'',
            u'type_id': 97
        }
        self.assertEquals(Attribute.objects.get(news_item__id=1).varchar01, u'Hello')

    def testSetAllAttributesNull(self):
        # If you assign to NewsItem.attributes and the dictionary
        # doesn't include a value for every field, a None/NULL will be
        # inserted for values that aren't represented in the
        # dictionary.
        ni = NewsItem.objects.get(id=1)
        ni.attributes = {u'arrests': False}
        ni = NewsItem.objects.get(id=1)
        self.assertEquals(ni.attributes['arrests'], False)
        self.assertEquals(ni.attributes['beat'], None)
        self.assertEquals(ni.attributes['block_id'], None)
        self.assertEquals(ni.attributes['case_number'], None)
        self.assertEquals(ni.attributes['crime_date'], None)
        self.assertEquals(ni.attributes['crime_time'], None)
        self.assertEquals(ni.attributes['domestic'], None)
        self.assertEquals(ni.attributes['is_outdated'], None)
        self.assertEquals(ni.attributes['location_id'], None)
        self.assertEquals(ni.attributes['police_id'], None)
        self.assertEquals(ni.attributes['status'], None)
        self.assertEquals(ni.attributes['type_id'], None)

    def testSetSingleAttribute1(self):
        # Setting a single attribute will result in an immediate query setting
        # just that attribute.
        ni = NewsItem.objects.get(id=1)
        self.assertEquals(ni.attributes['case_number'], u'case number 1')
        ni.attributes['case_number'] = u'Hello'
        self.assertEquals(Attribute.objects.get(news_item__id=1).varchar01, u'Hello')

    def testSetSingleAttribute2(self):
        # Setting single attributes works even if you don't access them first.
        ni = NewsItem.objects.get(id=1)
        ni.attributes['case_number'] = u'Hello'
        self.assertEquals(Attribute.objects.get(news_item__id=1).varchar01, u'Hello')

    def testSetSingleAttribute3(self):
        # Setting a single attribute will result in the value being cached.
        ni = NewsItem.objects.get(id=1)
        self.assertEquals(ni.attributes['case_number'], u'case number 1')
        ni.attributes['case_number'] = u'Hello'
        self.assertEquals(ni.attributes['case_number'], u'Hello')

    def testSetSingleAttribute4(self):
        # Setting a single attribute will result in the value being cached, even
        # if you don't access the attribute first.
        ni = NewsItem.objects.get(id=1)
        ni.attributes['case_number'] = u'Hello'
        self.assertEquals(ni.attributes['case_number'], u'Hello')

    def testSetSingleAttributeNumQueries(self):
        # When setting an attribute, the system will only use a single query --
        # i.e., it won't have to retrieve the attributes first simply because
        # code accessed the NewsItem.attributes attribute.

        # Turn DEBUG on and reset queries, so we can keep track of queries.
        from django.db import connection
        connection.queries = []
        with self.settings(DEBUG=True):
            ni = NewsItem.objects.get(id=1)
            ni.attributes['case_number'] = u'Hello'
            self.assertEquals(len(connection.queries), 3)

        connection.queries = []

    def testBlankAttributes(self):
        # If a NewsItem has no attributes set, accessing
        # NewsItem.attributes will return an empty dictionary.
        Attribute.objects.filter(news_item__id=1).delete()
        ni = NewsItem.objects.get(id=1)
        self.assertEquals(ni.attributes, {})

    def testSetAttributesFromBlank(self):
        # When setting attributes on a NewsItem that doesn't have
        # attributes yet, the underlying implementation will use an
        # INSERT statement instead of an UPDATE.
        Attribute.objects.filter(news_item__id=1).delete()
        ni = NewsItem.objects.get(id=1)
        ni.attributes = {
            u'arrests': False,
            u'beat': 214,
            u'block_id': 25916,
            u'case_number': u'Hello',
            u'crime_date': datetime.date(2006, 9, 19),
            u'crime_time': None,
            u'domestic': False,
            u'is_outdated': True,
            u'location_id': 66,
            u'police_id': None,
            u'status': u'',
            u'type_id': 97
        }
        self.assertEquals(Attribute.objects.get(news_item__id=1).varchar01, u'Hello')

    def testSetSingleAttributeFromBlank(self):
        # When setting a single attribute on a NewsItem that doesn't have
        # attributes yet, the underlying implementation will use an INSERT
        # statement instead of an UPDATE.
        Attribute.objects.filter(news_item__id=1).delete()
        ni = NewsItem.objects.get(id=1)
        ni.attributes['case_number'] = u'Hello'
        self.assertEquals(Attribute.objects.get(news_item__id=1).varchar01, u'Hello')

    def testAttributeFromBlankSanity(self):
        # Sanity check for munging attribute data from blank.
        Attribute.objects.filter(news_item__id=1).delete()
        ni = NewsItem.objects.get(id=1)
        self.assertEquals(ni.attributes, {})
        ni.attributes['case_number'] = u'Hello'
        self.assertEquals(ni.attributes['case_number'], u'Hello')
        self.assertEquals(Attribute.objects.get(news_item__id=1).varchar01, u'Hello')

    def test_top_lookups__int(self):
        from ebpub.db.models import SchemaField
        sf = SchemaField.objects.get(name='beat')
        qs = NewsItem.objects.all()
        top_lookups = list(qs.top_lookups(sf, 2))
        self.assertEqual(len(top_lookups), 2)
        self.assertEqual(top_lookups[0]['count'], 2)
        self.assertEqual(top_lookups[0]['lookup'].slug, u'beat-64')
        self.assertEqual(top_lookups[1]['count'], 1)
        self.assertEqual(top_lookups[1]['lookup'].slug, u'beat-214')

    def test_top_lookups__m2m(self):
        from ebpub.db.models import SchemaField
        sf = SchemaField.objects.get(name='tags many-to-many')
        # from ebpub.db.bin.update_aggregates import update_aggregates
        # update_aggregates(sf.schema.id)
        qs = NewsItem.objects.all()
        top_lookups = list(qs.top_lookups(sf, 2))
        self.assertEqual(len(top_lookups), 2)
        self.assertEqual(top_lookups[0]['count'], 3)
        self.assertEqual(top_lookups[0]['lookup'].slug, u'tag-1')
        self.assertEqual(top_lookups[1]['count'], 2)
        self.assertEqual(top_lookups[1]['lookup'].slug, u'tag-2')


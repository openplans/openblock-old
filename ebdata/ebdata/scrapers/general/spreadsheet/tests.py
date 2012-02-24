#   Copyright 2012 OpenPlans and contributors
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


import django.test
import mock
import os
import unittest
from ebdata.retrieval.scrapers.tests import HERE

class TestCsvScraper(django.test.TestCase):

    fixtures = (os.path.join(HERE, 'fixtures', 'test_scraper_fixtures.json')
                ,)

    def _get_schema(self):
        from ebpub.db.models import Schema
        schema = Schema.objects.get(
            slug='scrapertest-news'
            )
        return schema

    def _make_scraper(self):
        from ..spreadsheet import retrieval
        scraper = retrieval.CsvListDetailScraper(None, None, use_cache=False)
        # Be quiet!
        scraper.logger = mock.Mock()
        scraper.schema = self._get_schema()
        return scraper

    def test_clean_list_record__no_info(self):
        scraper = self._make_scraper()
        cleaned = scraper.clean_list_record({})
        self.assertEqual(cleaned,
                         {'attributes': {}, 'schema': scraper.schema,
                          'location': None, 'location_name': None})

    def test_clean_list_record__ok(self):
        scraper = self._make_scraper()
        cleaned = scraper.clean_list_record({'title': 't1', 'description': 'd1'})
        self.assertEqual(cleaned, {'title': 't1', 'description': 'd1',
                                   'schema': scraper.schema,
                                   'location': None, 'location_name': None,
                                   'attributes': {}})

        cleaned = scraper.clean_list_record({'title': 't2', 'unknown': 'blah'})
        self.assertEqual(cleaned, {'title': 't2', 'schema': scraper.schema,
                                   'location': None, 'location_name': None,
                                   'attributes': {}})

        cleaned = scraper.clean_list_record({'title': 't3', 'attr1': 'a1'})
        self.assertEqual(cleaned, {'title': 't3', 'schema': scraper.schema,
                                   'location': None, 'location_name': None,
                                   'attributes': {'attr1': 'a1'}})

    @mock.patch('ebpub.db.models.logger')
    def test_save__no_info(self, mock_logger):
        scraper = self._make_scraper()
        result = scraper.save(None, {}, None)
        self.assertEqual(result['errors']['location_name'],
                         [u'This field is required.'])
        result = scraper.save(None, {'blah': 'blech'}, None)
        self.assertEqual(result['errors']['location_name'],
                         [u'This field is required.'])


    @mock.patch('ebpub.db.models.logger')
    def test_save__not_enough_info(self, mock_logger):
        info = {'title': 't1', 'description': 'd1', 'attr1': 'a1', 'bad': 'b1'}
        scraper = self._make_scraper()
        result = scraper.save(None, info, None)
        self.assert_(isinstance(result, dict))
        self.assertEqual(result['errors']['location_name'],
                         [u'This field is required.'])


    @mock.patch('ebpub.db.models.logger')
    def test_save__ok(self, mock_logger):
        info = {'title': 't1', 'description': 'd1', 'location_name': 'somewhere',
                'attributes': {'attr1': 'a1', 'bad1': 'b1'},
                'bad2': 'b2'}
        scraper = self._make_scraper()
        item = scraper.save(None, info, None)
        self.assertEqual(item.attributes['attr1'], 'a1')
        self.assertEqual(item.title, 't1')
        self.assertEqual(item.description, 'd1')
        self.failIf('bad1' in item.attributes)
        self.failIf(hasattr(item, 'bad2'))


def suite():
    import doctest
    from ..spreadsheet import retrieval
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCsvScraper)
    suite.addTest(doctest.DocTestSuite(retrieval, optionflags=doctest.ELLIPSIS))
    return suite

if __name__ == '__main__':
    unittest.main()

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
        schema = self._get_schema()
        scraper = retrieval.CsvListDetailScraper(None, None, use_cache=False,
                                                 schema_slug=schema.slug)
        # Be quiet!
        scraper.logger = mock.Mock()
        return scraper

    def test_clean_list_record__no_info(self):
        scraper = self._make_scraper()
        cleaned = scraper.clean_list_record({})
        self.assertEqual(cleaned,
                         {'attributes': {},
                          'location': None, 'location_name': None})

    def test_clean_list_record__ok(self):
        scraper = self._make_scraper()
        cleaned = scraper.clean_list_record({'title': 't1', 'description': 'd1'})
        self.assertEqual(cleaned, {'title': 't1',
                                   'description': 'd1',
                                   'location': None,
                                   'location_name': None,
                                   'attributes': {}})

        cleaned = scraper.clean_list_record({'title': 't2', 'unknown': 'blah'})
        self.assertEqual(cleaned, {'title': 't2',
                                   'location': None,
                                   'location_name': None,
                                   'attributes': {}})

        cleaned = scraper.clean_list_record({'title': 't3', 'attr1': 'a1'})
        self.assertEqual(cleaned, {'title': 't3',
                                   'location': None,
                                   'location_name': None,
                                   'attributes': {'attr1': 'a1'}})

    @mock.patch('ebpub.db.models.logger')
    def test_save__no_info(self, mock_logger):
        scraper = self._make_scraper()
        from ebdata.retrieval.scrapers.list_detail import SkipRecord
        with self.assertRaises(SkipRecord) as e:
            scraper.save(None, {}, None)
        self.assertEqual(e.exception.message['location_name'],
                          [u'This field is required.'])
        with self.assertRaises(SkipRecord) as e:
            scraper.save(None, {'blah': 'blech'}, None)
        self.assertEqual(e.exception.message['location_name'],
                          [u'This field is required.'])


    @mock.patch('ebpub.db.models.logger')
    def test_save__not_enough_info(self, mock_logger):
        from ebdata.retrieval.scrapers.list_detail import SkipRecord
        info = {'title': 't1', 'description': 'd1', 'attr1': 'a1', 'bad': 'b1'}
        scraper = self._make_scraper()
        with self.assertRaises(SkipRecord) as e:
            scraper.save(None, info, None)
        self.assertEqual(e.exception.message['location_name'],
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


    @mock.patch('ebdata.scrapers.general.spreadsheet.retrieval.open_url')
    def test_init_opens_files(self, mock_opener):
        from ..spreadsheet import retrieval
        schema = self._get_schema()
        scraper = retrieval.CsvListDetailScraper('foo.txt', 'bar.txt',
                                                 use_cache=False,
                                                 schema_slug=schema.slug)
        self.assertEqual(mock_opener.call_count, 2)
        self.assertEqual(mock_opener.call_args_list,
                         [(('foo.txt',),),
                          (('bar.txt',),)])


    def test_existing_record__default_unique_fields(self):
        scraper = self._make_scraper()
        record = {'title': 't1', 'location_name': 'ln1', 'description': 'd1',
                  'schema': self._get_schema(),
                  }
        from ebpub.db.models import NewsItem
        self.assertEqual(scraper.unique_fields, ())
        self.assertEqual(scraper.existing_record(record), None)
        ni = NewsItem.objects.create(**record)
        try:
            self.assertEqual(scraper.existing_record(record), ni)
        finally:
            ni.delete()

    def test_existing_record__unknown_field(self):
        scraper = self._make_scraper()
        record = {'title': 't1', 'location_name': 'ln1', 'description': 'd1',
                  'schema': self._get_schema(),
                  }
        from ebpub.db.models import NewsItem
        scraper.unique_fields = ('No Such Thing',)
        ni = NewsItem.objects.create(**record)
        try:
            self.assertEqual(scraper.existing_record(record), None)
        finally:
            ni.delete()

    def test_existing_record__changed_value(self):
        scraper = self._make_scraper()
        record = {'title': 't1', 'location_name': 'ln1', 'description': 'd1',
                  'schema': self._get_schema(),
                  }
        from ebpub.db.models import NewsItem
        scraper.unique_fields = ('location_name',)
        ni = NewsItem.objects.create(**record)
        try:
            self.assertEqual(scraper.existing_record(record), ni)
            record['location_name'] = 'ln2'
            self.assertEqual(scraper.existing_record(record), None)
        finally:
            ni.delete()


def suite():
    import doctest
    from ..spreadsheet import retrieval
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCsvScraper)
    suite.addTest(doctest.DocTestSuite(retrieval, optionflags=doctest.ELLIPSIS))
    return suite

if __name__ == '__main__':
    unittest.main()

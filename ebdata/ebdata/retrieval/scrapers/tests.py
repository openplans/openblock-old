#   Copyright 2012 OpenPlans, and contributors
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
#

import datetime
import django.test
import mock
import os
HERE = os.path.abspath(os.path.dirname(__file__))


class TestBaseScraper(django.test.TestCase):

    def _make_scraper(self):
        from ebdata.retrieval.scrapers.base import BaseScraper
        scraper = BaseScraper(use_cache=False)
        # Be quiet!
        scraper.logger = mock.Mock()
        return scraper

    @mock.patch('ebdata.retrieval.scrapers.base.full_geocode')
    def test_geocode__ok(self, mock_full_geocode):
        mock_full_geocode.return_value = {'result': 'something', 'type': 'address'}
        scraper = self._make_scraper()
        self.assertEqual(scraper.geocode('somewhere'),
                         'something')

    @mock.patch('ebdata.retrieval.scrapers.base.full_geocode')
    def test_geocode__error(self, mock_full_geocode):
        from ebpub.geocoder.base import GeocodingException, ParsingError

        mock_full_geocode.side_effect = GeocodingException()
        scraper = self._make_scraper()
        self.assertEqual(scraper.geocode('somewhere'), None)

        mock_full_geocode.side_effect = ParsingError()
        scraper = self._make_scraper()
        self.assertEqual(scraper.geocode('somewhere'), None)

    @mock.patch('ebdata.retrieval.scrapers.base.parse_addresses')
    @mock.patch('ebdata.retrieval.scrapers.base.full_geocode')
    def test_geocode_if_needed__geocode_errors(self, mock_full_geocode, mock_parse):
        mock_full_geocode.side_effect = Exception()
        mock_parse.return_value = [('somewhere', None)]
        scraper = self._make_scraper()
        result = scraper.geocode_if_needed(None, 'somewhere')
        self.assertEqual(result, (None, 'somewhere'))

    @mock.patch('ebpub.geocoder.reverse.reverse_geocode')
    def test_geocode_if_needed__reverse_errors(self, mock_reverse):
        from ebpub.geocoder.reverse import ReverseGeocodeError
        mock_reverse.side_effect = ReverseGeocodeError()
        scraper = self._make_scraper()
        mock_point = mock.Mock()
        result = scraper.geocode_if_needed(mock_point, None)
        self.assertEqual(result, (mock_point, None))

    @mock.patch('ebpub.geocoder.reverse.reverse_geocode')
    def test_geocode_if_needed__point_only(self, mock_reverse):
        scraper = self._make_scraper()
        mock_block = mock.Mock(pretty_name='123 Anywhere St')
        mock_reverse.return_value = (mock_block, 0.0)
        mock_point = mock.Mock()
        result = scraper.geocode_if_needed(mock_point, None)
        self.assertEqual(result,  (mock_point, '123 Anywhere St'))

    @mock.patch('ebdata.retrieval.scrapers.base.BaseScraper.geocode')
    def test_geocode_if_needed__name_only(self, mock_geocode):
        scraper = self._make_scraper()
        mock_point = object()
        mock_geocode.return_value = {'point': mock_point}
        result = scraper.geocode_if_needed(None, '123 Anywhere St')
        self.assertEqual(result,  (mock_point, '123 Anywhere St'))

    @mock.patch('ebdata.retrieval.scrapers.base.BaseScraper.geocode')
    def test_geocode_if_needed__name_and_text(self, mock_geocode):
        scraper = self._make_scraper()
        mock_point = object()
        mock_geocode.return_value = {'point': mock_point}
        result = scraper.geocode_if_needed(None, '123 Anywhere St', 'Unused')
        self.assertEqual(result,  (mock_point, '123 Anywhere St'))

    @mock.patch('ebdata.retrieval.scrapers.base.BaseScraper.geocode')
    def test_geocode_if_needed__text_only(self, mock_geocode):
        scraper = self._make_scraper()
        mock_point = object()
        mock_geocode.return_value = {'point': mock_point,
                                     'address': 'The Real Address'}
        result = scraper.geocode_if_needed(None, None, '123 Anywhere St')
        self.assertEqual(result,  (mock_point, 'The Real Address'))

    def test_parse_html(self):
        html = '''
           <html><head><title>Hello</title></head>
              <body><h1>Yes.</h1></body>
           </html>
        '''
        scraper = self._make_scraper()
        parsed = scraper.parse_html(html)
        self.assertEqual(parsed.find('//h1').text, 'Yes.')


    def test_fetch_data(self):
        scraper = self._make_scraper()
        scraper.retriever = mock.Mock()
        args=('arg1',)
        kwargs={'arg2': 'val2'}
        scraper.fetch_data(*args, **kwargs)
        self.assertEqual(scraper.retriever.fetch_data.call_count, 1)
        self.assertEqual(scraper.retriever.fetch_data.call_args,
                         (args, kwargs))
        scraper.get_html(*args, **kwargs)
        self.assertEqual(scraper.retriever.fetch_data.call_count, 2)
        self.assertEqual(scraper.retriever.fetch_data.call_args,
                         (args, kwargs))


class TestCreateNewsitem(django.test.TestCase):

    # Use hardcoded path so I don't have to make this into an app
    # or mess with settings just to get a test fixture.
    fixtures = (os.path.join(HERE, 'fixtures', 'test_scraper_fixtures.json')
                ,)

    def _make_scraper(self):
        from ebdata.retrieval.scrapers.base import BaseScraper
        scraper = BaseScraper(use_cache=False)
        # Be quiet!
        scraper.logger = mock.Mock()
        return scraper

    def _get_schema(self):
        from ebpub.db.models import Schema
        schema = Schema.objects.get(
            slug='scrapertest-news'
            )
        return schema

    def test_create_newsitem(self):
        scraper = self._make_scraper()
        schema = self._get_schema()
        item = scraper.create_newsitem({'attr1': 'value 1'},
                                       title=u'Test Title',
                                       item_date=datetime.date(2012, 2, 1),
                                       location_name='123 Anywhere',
                                       schema=schema)
        self.assert_(item.id)
        self.assertEqual(item.title, u'Test Title')
        self.assertEqual(item.location, None)
        self.assertEqual(item.attributes['attr1'], 'value 1')

    def test_update_existing(self):
        scraper = self._make_scraper()
        schema = self._get_schema()
        item = scraper.create_newsitem({'attr1': 'value 1'},
                                       title=u'Test Title',
                                       item_date=datetime.date(2012, 2, 1),
                                       location_name='123 Anywhere',
                                       schema=schema)

        # No update... passes silently.
        scraper.update_existing(item, {}, {})
        # Update with data.
        scraper.update_existing(item, {'title': u'New Title'}, {'attr1': u'New Value'})
        self.assertEqual(item.title, u'New Title')
        self.assertEqual(item.attributes['attr1'], u'New Value')

    def test_create_or_update(self):
        from ebpub.db.models import NewsItem
        scraper = self._make_scraper()
        schema = self._get_schema()
        kwargs = {'title': 'Veeblefetzer',
                  'location_name': 'Potrzebie',
                  'item_date': datetime.date(2012, 01, 01),
                  'schema': schema}
        attrs = {'attr1': 'Potrzebie'}
        # Create.
        self.assertEqual(NewsItem.objects.filter(title=kwargs['title']).count(),
                         0)
        scraper.create_or_update(None, attrs, **kwargs)

        self.assertEqual(NewsItem.objects.filter(title=kwargs['title']).count(),
                         1)
        item = NewsItem.objects.get(**kwargs)

        # Update.
        scraper.create_or_update(item, attrs, title='Kurtzman')
        self.assertEqual(item.title, 'Kurtzman')



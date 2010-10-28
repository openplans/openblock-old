"""
RANDOM DOC NOTES:

- read docstrings in ebdata.retrieval.scrapers.list_detail for more
  implementation info on this type of scraper

"""

from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
from ebdata.retrieval.scrapers.list_detail import StopScraping, SkipRecord
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.textmining.treeutils import preprocess_to_string
from ebpub.db.models import NewsItem

import datetime
import math
import re

BASE_URL = 'https://seeclickfix.com/api/'
FEED_URL = BASE_URL + 'issues.rss?at=Boston,+MA&sort=issues.created_at&direction=DESC'

address_re = re.compile(r'Address: (.*?)<br\s+/>')
rating_re = re.compile(r'\s+Rating:\s+(\d+)\s*')


class SeeClickFixNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):
    """
    For all of these methods, see docstrings in
    ebdata.retrieval.scrapers.list_detail.ListDetailScraper
    """

    schema_slugs = ('issues',)
    has_detail = True

    def list_pages(self):
        self.logger.debug('wheee!')
        # Fetch the feed, paginating if necessary.
        # See API docs at
        # http://help.seeclickfix.com/faqs/api/listing-issues
        max_per_page = 200
        max_pages = 10

        # First, figure out how long it's been since the last scrape;
        # seeclickfix has a 'start' option in hours.  The idea is not
        # to be precise, but to get everything we haven't seen yet and
        # not much that we have seen. So we'll discard microseconds
        # and round up.

        delta = datetime.datetime.now() - self.last_updated_time()
        hours_ago = math.ceil((delta.seconds / 3600.0) + (delta.days * 24))
        for page in range(1, max_pages + 1):
            feed_url = FEED_URL + '&start=%d&page=%d&num_results=%d' % (
                hours_ago, page, max_per_page)
            yield self.fetch_data(feed_url)

    def existing_record(self, cleaned_list_record):
        url = cleaned_list_record['id'].replace('https:', 'http:')
        qs = NewsItem.objects.filter(schema__id=self.schema.id, url=url)
        try:
            return qs[0]
        except IndexError:
            return None

    def detail_required(self, list_record, old_record):
        # Always fetch detail pages.
        return True

    def get_detail(self, record):
        # There's no direct link to the JSON detail page,
        # but we can construct one by munging the GUID link.
        url = record['guid'].replace('.html', '.json')
        return self.fetch_data(url)

    def parse_detail(self, page, list_record):
        from django.utils import simplejson
        return simplejson.loads(page)[0]

    def get_location(self, record):
        from django.contrib.gis.geos import Point
        lon = record['lng']
        lat = record['lat']
        return Point(lon, lat)

    def clean_detail_record(self, record):
        location = self.get_location(record)
        # XXX try self.safe_location? see newsitem_list_detail

        # This is a common error in some data sources we've seen...
        if location and (location.x == 0.0 and location.y == 0.0):
            self.logger.warn("skipping %r as it has bad location 0,0" % record['summary'])
            raise SkipRecord

        item_date = datetime.datetime.strptime(record['created_at'],
                                               '%m/%d/%Y at %I:%M%p')
        item_date = item_date.date()

        url = 'http://seeclickfix.com/issues/%d.html' % record['issue_id']
        attributes = {'rating': record['rating'],
                      }

        result = dict(title=record['summary'],
                      description=record['description'],
                      item_date=item_date,
                      location=location,
                      location_name=record['address'],
                      url=url,
                      attributes=attributes,
                      )
        return result


    def save(self, old_record, list_record, detail_record):
        # if old_record is not None:
        #     self.logger.info("Skipping, we've already seen %s" % old_record)
        #     return #raise StopScraping()

        attributes = detail_record.pop('attributes', None)
        self.create_or_update(old_record, attributes, **detail_record)



if __name__ == "__main__":
    TESTING = True
    if TESTING:
        from ebdata.retrieval import log_debug
        import pprint
        for info in SeeClickFixNewsFeedScraper().raw_data():
            pprint.pprint(info['detail'])
    else:
        SeeClickFixNewsFeedScraper().update()


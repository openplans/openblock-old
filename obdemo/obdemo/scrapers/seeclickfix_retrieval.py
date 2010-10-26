"""
RANDOM DOC NOTES:

- read docstrings in ebdata.retrieval.scrapers.list_detail for more
  implementation info on this type of scraper

"""

from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
from ebdata.retrieval.scrapers.list_detail import StopScraping
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.textmining.treeutils import preprocess_to_string
from ebpub.db.models import NewsItem

import datetime
import math
import re

BASE_URL = 'https://seeclickfix.com/api/'
LIST_URL = BASE_URL + 'issues.rss?at=Boston,+MA'

address_re = re.compile(r'Address: (.*?)<br\s+/>')
rating_re = re.compile(r'\s+Rating:\s+(\d+)\s*')


def get_unique_fields(list_record):
    # not necessarily primary key, but for this script's purposes
    # these are the fields that in combination uniquely idenfity
    # an article.

    # TODO: 'id' is all we need for uniqueness, but what i'm doing
    # here is really cleaning?

    date = datetime.date(*list_record['updated_parsed'][:3])
    summary_detail = list_record['summary_detail']['value']
    addr = address_re.search(summary_detail)
    if addr:
        addr = addr.group(1)
        location_name = ', '.join([part.strip() for part in addr.split(',')])
    else:
        location_name = u''

    return dict(id=list_record['id'], item_date=date,
                location_name=location_name,
                title=list_record['title'],
                )


class SeeClickFixNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):
    schema_slugs = ('issues',)
    has_detail = False

    def list_pages(self):
        # See API docs at
        # http://help.seeclickfix.com/faqs/api/listing-issues
        # paginate if necessary.
        max_per_page = 1000
        max_pages = 10
        # First, figure out how long it's been since the last scrape;
        # seeclickfix has a 'start' option in hours.
        # We'll discard microseconds and round up.
        # The idea is not to be precise, but to get everything we haven't
        # seen yet and not much that we have seen.
        delta = datetime.datetime.now() - self.last_updated_time()
        hours_ago = math.ceil((delta.seconds / 3600.0) + (delta.days * 24))
        for page in range(1, max_pages + 1):
            url = LIST_URL + '&start=%d&page=%d&num_results=%d' % (
                hours_ago, page, max_per_page)
            yield self.get_html(url)

    def existing_record(self, list_record):
        # XXX Where does self.schema_fields come from??
        qs = NewsItem.objects.filter(schema__id=self.schema.id)
        qs = qs.by_attribute(self.schema_fields['guid'], list_record['id'])
        try:
            return qs[0]
        except IndexError:
            return None

    def save(self, old_record, list_record, detail_record):
        if old_record is not None:
            self.logger.info("Stopping, we've already seen %s" % old_record)
            raise StopScraping()

        kwargs = get_unique_fields(list_record)

        location = self.get_location(list_record)

        if (location.x, location.y) == (0,0, 0.0):
            self.logger.warn("skipping %r as it has bad location 0,0" % list_record['title'])
            return

        # remove address and rating from summary.
        # TODO: do in cleaner methods?
        summary_detail = list_record['summary_detail']['value']
        content = list_record['summary']
        content = address_re.sub('', content)
        rating = rating_re.search(content)
        attributes = {'guid': list_record['id']}
        if rating:
            rating = int(rating.group(1))
            attributes['rating'] = rating
            content = rating_re.sub('', content)

        content = preprocess_to_string(content, drop_tags=('p', 'br', 'b',))
        kwargs['description'] = content

        # XXX try self.safe_location? see newsitem_list_detail
        kwargs['location'] = location

        self.create_or_update(old_record, attributes, **kwargs)



if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    SeeClickFixNewsFeedScraper().update()

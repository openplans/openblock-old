"""

Boston city press release scraper.

http://www.cityofboston.gov/news/
Example: http://www.cityofboston.gov/news/default.aspx?id=3910
"""

from ebdata.nlp.addresses import parse_addresses
from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
from ebdata.retrieval.scrapers.list_detail import SkipRecord
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.textmining.treeutils import text_from_html
from ebpub.db.models import NewsItem
from ebpub.geocoder import SmartGeocoder
from ebpub.geocoder.base import GeocodingException
from utils import log_exception
import logging
import datetime


class BPDNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):

    schema_slugs = ('police-reports',)
    has_detail = False

    # Can't find a way to specify number of items.
    url = 'http://www.bpdnews.com/feed/'

    def list_pages(self):
        yield self.fetch_data(self.url)

    def existing_record(self, record):
        url = record['link']
        qs = NewsItem.objects.filter(schema__id=self.schema.id, url=url)
        try:
            return qs[0]
        except IndexError:
            return None

    def clean_list_record(self, record):
        if record['title'].startswith(u'Boston 24'):
            # We don't include the summary posts.
            # TODO: the 'Boston 24' tag indicates posts with aggregate
            # daily stats.  Make a separate schema for the aggregates,
            # with attributes like those used in
            # everyblock/everyblock/cities/nyc/crime_aggregate/retrieval.py.
            # Or maybe not: these are citywide, not by precinct.
            # So what would be the Location?  Whole city??
            self.logger.info("boston daily crime stats, we don't know how to "
                             "handle these yet")
            raise SkipRecord
        return record

    def save(self, old_record, list_record, detail_record):
        # TODO: move some of this to clean_list_record?
        date = datetime.date(*list_record['updated_parsed'][:3])

        # Get the precinct from the tags.
        precincts = ['A1', 'A7', 'B2', 'B3', 'C11', 'C6', 'D14', 'D4',
                     'E13', 'E18', 'E5']
        precinct = None
        tags = [t['term'] for t in list_record['tags']]
        if not tags:
            return

        for precinct in tags:
            if precinct in precincts:
                # TODO: we need a LocationType for precincts, and shapes; and
                # then we could set newsitem.location_object to the Location
                # for this precinct.
                break

        if not precinct:
            self.logger.debug("no precinct found in tags %r" % tags)

        description = list_record['summary']

        full_description = list_record['content'][0]['value']
        full_description = text_from_html(full_description)

        addrs = parse_addresses(full_description)
        if not addrs:
            self.logger.info("no addresses found in %r %r" % (list_record['title'], 
                                                           list_record['link']))
            return

        location = None
        location_name = u''
        block = None

        # This feed doesn't provide geographic data; we'll try to
        # extract addresses from the text, and stop on the first
        # one that successfully geocodes.
        for addr, unused in addrs:
            addr = addr.strip()
            try:
                location = SmartGeocoder().geocode(addr)
            except GeocodingException:
                log_exception(level=logging.DEBUG)
                continue
            location_name = location['address']
            block = location['block']
            location = location['point']
            break
        else:
            self.logger.info("no addresses geocoded in %r" % list_record['title'])
            return

        kwargs = dict(item_date=date,
                      location=location,
                      location_name=location_name,
                      title=list_record['title'],
                      description=description,
                      url=list_record['link'],
                      )
        attributes = None
        self.create_or_update(old_record, attributes, **kwargs)


if __name__ == "__main__":
    #from ebdata.retrieval import log_debug
    BPDNewsFeedScraper().update()

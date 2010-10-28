"""
Boston city press release scraper.

http://www.cityofboston.gov/news/
Example: http://www.cityofboston.gov/news/default.aspx?id=3910
"""

from django.contrib.gis.geos import Point
from ebdata.nlp.addresses import parse_addresses
from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.textmining.treeutils import preprocess_to_string
from ebpub.db.models import NewsItem
import datetime


class BPDNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):

    # TODO: these should have a different schema, like 'police-reports'

    schema_slugs = ('police-reports',)
    has_detail = False

    url = 'http://www.bpdnews.com/feed/'

    def list_pages(self):
        yield self.fetch_data(self.url)

    def existing_record(self, record):
        kwargs = self.unique_fields(record)
        try:
            qs = NewsItem.objects.filter(schema__id=self.schema.id, **kwargs)
            # TODO: something like this once we have precinct attributes:
            #qs = qs.by_attribute(self.schema_fields['precinct'], record['precinct_obj'].id)
            return qs[0]
        except IndexError:
            return None
        return None

    def save(self, old_record, list_record, detail_record):
        # Extract the precinct from the tags.

        kwargs = self.unique_fields(list_record)

        attributes = None

        # TODO: this seems like a really common pattern to put in a base class.
        if old_record:
            self.update_existing(old_record, kwargs, attributes or {})
            self.logger.info("Updated")
        else:
            self.create_newsitem(attributes=attributes, **kwargs)
            self.logger.info("Created")
        if old_record:
            return

    def unique_fields(self, list_record):
        # not necessarily primary key, but for this script's purposes
        # these are the fields that in combination uniquely idenfity
        # an article.
        date = datetime.date(*list_record['updated_parsed'][:3])
        precincts = ['A1', 'A7', 'B2', 'B3', 'C11', 'C6', 'D14', 'D4',
                     'E13', 'E18', 'E5']
        precinct = None
        tags = [t['term'] for t in list_record['tags']]
        if not tags:
            return
        for precinct in tags:
            if precinct in precincts:
                # TODO: we need a LocationType for precincts, and shapes; and
                # then we can set newsitem.location_object to the Location
                # for this precinct.
                break

        if not precinct:
            self.logger.debug("no precinct found in tags %r" % tags)

        if 'Boston 24' in tags:
            # TODO: the 'Boston 24' tag indicates posts with aggregate
            # daily stats.  Make a separate schema for aggregates,
            # with attributes like those used in
            # everyblock/everyblock/cities/nyc/crime_aggregate/retrieval.py.
            # These are citywide though, not by precinct.
            # So what would be the Location?  Whole city??
            self.logger.info("boston daily crime stats, we don't know how to "
                             "handle these yet")

        description = list_record['content'][0]['value']
        # TODO: we should have a stock 'clean up html' function.
        description = preprocess_to_string(
            description,
            drop_tags=('a', 'area', 'b', 'center', 'font', 'form', 'img', 'input', 'p', 'strong', 'map', 'small', 'span', 'sub', 'sup', 'topic', 'u'),
            drop_trees=('applet', 'button', 'embed', 'iframe', 'object', 'select', 'textarea'),
            drop_attrs=('background', 'border', 'cellpadding', 'cellspacing', 'class', 'clear', 'id', 'rel', 'style', 'target'))
        from ebdata.retrieval.utils import convert_entities
        description = convert_entities(description)
        #description = description.replace('&nbsp;', ' ').replace('&#160;', ' ')

        addrs = parse_addresses(description)
        if not addrs:
            self.logger.info("no addresses found in %r" % list_record['title'])

        location = None
        location_name = u''
        for addr, unused in addrs:
            addr = addr.strip()
            try:
                from geocoder_hack import quick_dirty_fallback_geocode
                x, y = quick_dirty_fallback_geocode(addr)
                if (x, y) != (None, None):
                    location = Point((float(x), float(y)))
                    location_name = addr.title()
            except:
                print "ugh, %r" % addr
                # XXX log something

        return dict(item_date=date,
                    location=location,
                    location_name=location_name,
                    title=list_record['title'],
                    description=description,
                    )

if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    BPDNewsFeedScraper().update()

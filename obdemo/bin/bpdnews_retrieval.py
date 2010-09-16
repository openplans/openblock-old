"""
Boston city press release scraper.

http://www.cityofboston.gov/news/
Example: http://www.cityofboston.gov/news/default.aspx?id=3910
"""

from django.contrib.gis.geos import Point
from ebdata.nlp.addresses import parse_addresses
from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.textmining.treeutils import make_tree, preprocess
from geopy import geocoders
import datetime
import lxml


class BPDNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):

    # TODO: these should have a different schema, like 'police-reports'

    schema_slugs = ('local-news',)
    has_detail = False

    url = 'http://www.bpdnews.com/feed/'

    def list_pages(self):
        yield self.get_html(self.url)

    def existing_record(self, record):
        # TODO
        return None

    def save(self, old_record, list_record, detail_record):
        content = list_record['content'][0]['value']
        tree = make_tree(content)
        tree = preprocess(
            tree,
            drop_tags=('a', 'area', 'b', 'center', 'font', 'form', 'img', 'input', 'p', 'strong', 'map', 'small', 'span', 'sub', 'sup', 'topic', 'u'),
            drop_trees=('applet', 'button', 'embed', 'iframe', 'object', 'select', 'textarea'),
            drop_attrs=('background', 'border', 'cellpadding', 'cellspacing', 'class', 'clear', 'id', 'rel', 'style', 'target'))
        text = lxml.etree.tostring(tree)
        text = text.replace('&nbsp;', ' ').replace('&#160;', ' ')

        addrs = parse_addresses(text)
        if not addrs:
            print "no addresses found in %r" % list_record['title']
            return

        for addr, unused in addrs:
            try:
                from geocoder_hack import quick_dirty_fallback_geocode
                #location = SmartGeocoder().geocode(addr)
                lon, lat = quick_dirty_fallback_geocode(addr)
                if (lon, lat) != (None, None):
                    break
            except:
                print "ugh, %r" % addr
                location = None
                # XXX log something
                return

        self.create_newsitem(
            attributes=None,
            title=list_record['title'],
            description=list_record['summary_detail']['value'],
            item_date=datetime.date(*list_record['updated_parsed'][:3]),
            location_name=addr.title(),
        )
        
        
if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    BPDNewsFeedScraper().update()

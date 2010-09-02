"""
Boston city press release scraper.

http://www.cityofboston.gov/news/
Example: http://www.cityofboston.gov/news/default.aspx?id=3910
"""

from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper

import re

class BPDNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):
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
        from ebdata.textmining.treeutils import make_tree, preprocess
        tree = make_tree(content)
        tree = preprocess(
            tree,
            drop_tags=('a', 'area', 'b', 'center', 'font', 'form', 'img', 'input', 'p', 'strong', 'map', 'small', 'span', 'sub', 'sup', 'topic', 'u'),
            drop_trees=('applet', 'button', 'embed', 'iframe', 'object', 'select', 'textarea'),
            drop_attrs=('background', 'border', 'cellpadding', 'cellspacing', 'class', 'clear', 'id', 'rel', 'style', 'target'))
        import lxml
        text = lxml.etree.tostring(tree)
        text = text.replace('&nbsp;', ' ').replace('&#160;', ' ')

        from ebdata.nlp.addresses import parse_addresses
        addrs = parse_addresses(text)
        from ebpub.geocoder.base import SmartGeocoder
        for addr, unused in addrs:
            try:
                location = SmartGeocoder().geocode(addr)
            except:
                print "ugh, %r" % addr
                location = None
                # XXX log something

        attributes = {}
        from ebpub.utils.dates import parse_date
        self.create_newsitem(
            attributes,
            title=list_record['title'],
            description=list_record['summary_detail']['value'],
            item_date=parse_date(list_record['updated'], '%a, %d %b %Y %H:%M:%S +0000'),
            location_name=addr.title(),
        )
        
        
if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    BPDNewsFeedScraper().update()

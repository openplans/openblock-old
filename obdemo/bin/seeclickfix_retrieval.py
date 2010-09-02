from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
from django.contrib.gis.geos import Point


base_url = 'https://seeclickfix.com/api/'

list_url = base_url + 'issues.rss?at=Boston,+MA'




class SeeClickFixNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):
    schema_slugs = ('local-news',) # TODO: make another type
    has_detail = False

    url = list_url

    def list_pages(self):
        yield self.get_html(self.url)

    def existing_record(self, record):
        # TODO
        return None

    def save(self, old_record, list_record, detail_record):
        summary_detail = list_record['summary_detail']['value']
        content = list_record['summary'] 
        # remove address and rating from content, i guess.
        content = content.replace(summary_detail, '')
        import re
        address_re = re.compile(r'Address: (.*?)<br />')
        addr = address_re.search(summary_detail)
        if addr:
            addr = addr.group(1)
            location_name = ', '.join([part.strip() for part in addr.split(',')])
        else:
            location_name = u''
        import datetime
        date = datetime.date(*list_record['updated_parsed'][:3])
        title = list_record['title']
        location = Point((float(list_record['geo_lat']),
                          float(list_record['geo_long'])))

        if (location.x, location.y) == (0,0, 0.0):
            print "skipping %r as it has bad location 0,0" % title
            return
        self.create_newsitem(
            attributes=None,
            title=u'SeeClickFix: ' + title,
            description=list_record['summary_detail']['value'],
            item_date=date,
            location_name=location_name,
            location=location,
        )
        
        
if __name__ == "__main__":
    #from ebdata.retrieval import log_debug
    SeeClickFixNewsFeedScraper().update()

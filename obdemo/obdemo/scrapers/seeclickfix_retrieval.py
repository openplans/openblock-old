from django.contrib.gis.geos import Point
from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.textmining.treeutils import preprocess_to_string
from ebpub.db.models import NewsItem
import re

BASE_URL = 'https://seeclickfix.com/api/'
LIST_URL = base_url + 'issues.rss?at=Boston,+MA'

address_re = re.compile(r'Address: (.*?)<br\s+/>')
rating_re = re.compile(r'\s+Rating:\s+(\d+)\s*')



class SeeClickFixNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):
    schema_slugs = ('issues',)
    has_detail = False

    url = LIST_URL

    def list_pages(self):
        yield self.get_html(self.url)

    def existing_record(self, list_record):
        unique_fields = self.unique_fields(list_record)
        qs = NewsItem.objects.filter(schema__id=self.schema.id, **unique_fields)
        try:
            return qs[0]
        except IndexError:
            return None

    def save(self, old_record, list_record, detail_record):
        kwargs = self.unique_fields(list_record)

        location = Point((float(list_record['geo_long']),
                          float(list_record['geo_lat'])))

        if (location.x, location.y) == (0,0, 0.0):
            print "skipping %r as it has bad location 0,0" % list_record['title']
            return

        # remove address and rating from summary.
        summary_detail = list_record['summary_detail']['value']
        content = list_record['summary']
        content = address_re.sub('', content)
        rating = rating_re.search(content)
        attributes = None
        if rating:
            rating = int(rating.group(1))
            attributes = {'rating': rating}
            content = rating_re.sub('', content)

        content = preprocess_to_string(content, drop_tags=('p', 'br', 'b',))
        kwargs.update(dict(description=content,
                           location=location,
                           ))
        if old_record:
            self.update_existing(old_record, kwargs, attributes)
        else:
            self.create_newsitem(attributes=attributes, **kwargs)

    def unique_fields(self, list_record):
        # not necessarily primary key, but for this script's purposes
        # these are the fields that in combination uniquely idenfity
        # an article.
        import datetime
        date = datetime.date(*list_record['updated_parsed'][:3])
        summary_detail = list_record['summary_detail']['value']
        addr = address_re.search(summary_detail)
        if addr:
            addr = addr.group(1)
            location_name = ', '.join([part.strip() for part in addr.split(',')])
        else:
            location_name = u''

        return dict(item_date=date,
                    location_name=location_name,
                    title=list_record['title'],
                    )


if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    SeeClickFixNewsFeedScraper().update()

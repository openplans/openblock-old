from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import simplejson
from ebdata.retrieval.scrapers.list_detail import StopScraping, SkipRecord
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper, local_tz
from ebdata.retrieval.utils import convert_entities
from ebpub.db.models import NewsItem
import datetime
from ebpub.metros.allmetros import get_metro

api_key = settings.MEETUP_API_KEY

# docs at http://www.meetup.com/meetup_api/docs/2/open_events/

class MeetupScraper(NewsItemListDetailScraper):

    logname = 'meetup_retrieval'
    has_detail = False
    max_records_per_scrape = 2000

    def __init__(self, options):
        self.api_key = settings.MEETUP_API_KEY
        self.options = options
        self.schema_slugs = [options.schema]
        self.records_seen = 0
        super(MeetupScraper, self).__init__()

    def list_pages(self):
        """generate page strings."""
        # Result of each iteration is a JSON string.
        from ebpub.db.models import Location
        metro = get_metro()
        city, state = metro['city_name'], metro['state']
        for zipcode in Location.objects.filter(location_type__slug='zipcodes'):
            params = dict(zip=zipcode.slug, key=api_key, city=city, state=state,
                          country='US')
            # Result of each iteration is a JSON string.
            pagenum = 0
            pages = float('inf')
            while pagenum < pages:
                self.logger.info("Page %s for zip code %s" % (pagenum, zipcode.slug))
                params['offset'] = pagenum
                url = 'https://api.meetup.com/2/open_events?key=%(key)s&state=%(state)s&city=%(city)s&country=%(country)s&zip=%(zip)s&page=200&offset=%(offset)s' % params
                page = self.fetch_data(url)
                pagenum += 1
                yield page

    def parse_list(self, page):
        # parse a single detail string page into record dicts
        results = None
        for encoding in ('utf8', 'cp1252', 'latin-1'):
            try:
                results = simplejson.loads(page, encoding).get('results', [])
                self.logger.info("Decoding using %s" % encoding)
                break
            except UnicodeDecodeError:
                self.logger.warn("Failed to decode using %s" % encoding)
                continue
        if not results:
            raise StopScraping("Nothing found on page")

        for result in results:
            if self.records_seen > self.max_records_per_scrape:
                raise StopScraping("We've reached %d records" % self.max_records_per_scrape)
            self.records_seen += 1
            yield result

    def clean_list_record(self, record):
        # clean up a record dict
        venue = record.get('venue', {})
        if not venue:
            raise SkipRecord("No venue")
        location_name_parts = [venue.get(key, '').strip() for key in
                               ('address_1', 'address_2', 'city', 'state', 'zip')]
        location_name = ', '.join([p for p in location_name_parts if p])
        event_time = datetime.datetime.fromtimestamp(record['time'] / 1000.0, local_tz)

        cleaned = {'title': convert_entities(record['name']),
                   'description': convert_entities(record.get('description', '')),
                   'location_name': location_name,
                   'location': Point(venue['lon'],
                                     venue['lat']),
                   'url': record['event_url'],
                   'item_date': event_time.date(),
                   }
        attributes = {'venue_phone': venue.get('phone', ''),
                      'venue_name': convert_entities(venue.get('name', '')),
                      'start_time': event_time.time(),
                      'group_name': record['group']['name'],
                      }
        cleaned['_attributes'] = attributes
        return cleaned


    def existing_record(self, record):
        # check if the CLEANED record dict matches a NewsItem
        try:
            item = NewsItem.objects.get(schema=self.schema, url=record['url'])
            return item
        except NewsItem.DoesNotExist:
            return None

    def save(self, old_record, list_record, detail_record):
        attributes = list_record.pop('_attributes')
        self.create_or_update(old_record, attributes, **list_record)


def main(argv=None):
    import sys
    if argv is None:
        argv = sys.argv[1:]
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option(
        "--schema", help="Slug of schema to use. Default is 'meetups'.",
        action='store', default='meetups',
        )

    options, args = parser.parse_args(argv)
    scraper = MeetupScraper(options)
    scraper.update()

if __name__ == '__main__':
    main()

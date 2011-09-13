from BeautifulSoup import UnicodeDammit
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import simplejson
from ebdata.retrieval.scrapers.list_detail import StopScraping, SkipRecord
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper, local_tz
from ebdata.textmining.treeutils import text_from_html

from ebpub.db.models import NewsItem
import datetime
from ebpub.metros.allmetros import get_metro
api_key = settings.MEETUP_API_KEY

# docs at http://www.meetup.com/meetup_api/docs/2/open_events/

class MeetupScraper(NewsItemListDetailScraper):

    logname = 'meetup_retrieval'
    has_detail = False

    def __init__(self, options):
        self.api_key = settings.MEETUP_API_KEY
        self.options = options
        self.schema_slugs = [options.schema]
        self.records_seen = 0
        super(MeetupScraper, self).__init__()

    def list_pages(self):
        """generate page strings."""
        # Result of each iteration is a JSON structure.
        # Normally in list_detail scrapers we return a string,
        # and leave parsing to parse_list(); but here we need to
        # parse to figure out pagination.
        from ebpub.db.models import Location
        metro = get_metro()
        city, state = metro['city_name'], metro['state']
        # We rotate among zip codes, fetching one page at a time for
        # each, since it's possible/likely that we will hit a rate
        # limit; this way, all the zip codes should get *something*.
        zipcode_state = {}
        ratelimit_remaining = 99999
        while True:
            for zipcode in Location.objects.filter(location_type__slug='zipcodes'):
                zipcode_state.setdefault(zipcode, {'page': int(self.options.start_page),
                                                   'done': False})
                if zipcode_state[zipcode]['done']:
                    continue

                params = dict(zip=zipcode.slug, key=api_key, city=city, state=state,
                              country='US',
                              time='-1m,2m',
                              )
                pagenum = zipcode_state[zipcode]['page']
                self.logger.info("Page %s for zip code %s" % (pagenum, zipcode.slug))
                params['offset'] = pagenum
                url = 'https://api.meetup.com/2/open_events?key=%(key)s&state=%(state)s&city=%(city)s&country=%(country)s&zip=%(zip)s&page=200&offset=%(offset)s' % params
                page, headers = self.retriever.fetch_data_and_headers(url,
                                                                      raise_on_error=False
)
                ratelimit_remaining = int(headers.get('x-ratelimit-remaining', '9999'))
                if ratelimit_remaining <= 1:
                    # Apparently meetup says you have 1 hit remaining
                    # when they actually mean "this is the last one."
                    ratelimit_reset = int(headers.get('x-ratelimit-reset'))
                    self.handle_ratelimit_exceeded(ratelimit_reset)
                elif int(headers.get('status')) >= 400:
                    try:
                        body = simplejson.loads(page)
                        problem, code = body.get('problem'), body.get('code')
                    except simplejson.JSONDecodeError:
                        problem = page
                        code = ''
                    if code == 'limit':
                        self.handle_ratelimit_exceeded()
                    else:
                        msg = "Error %d. %s: %s" % (headers.get('status'), code, problem)
                        self.logger.error(msg)
                        raise StopScraping(msg)
                zipcode_state[zipcode]['page'] += 1
                # Parse.
                encoding = headers.get('content-type', '').split('charset=')[-1]
                try:
                    decoded = page.decode(encoding)
                except LookupError:
                    decoded = UnicodeDammit(page, smartQuotesTo='html').unicode
                parsed = simplejson.loads(decoded)
                # Are there more pages?
                if not parsed['meta'].get('next'):
                    zipcode_state[zipcode]['done'] = True
                    self.logger.info("Finished zip code %s" % zipcode)
                yield parsed

            if not False in [value['done'] for value in zipcode_state.values()]:
                self.logger.info("Finished all zip codes")
                break


    def handle_ratelimit_exceeded(self, reset_time=None):
        """
        Either sleep until rate limit expires, or exit,
        depending on options.
        """
        import time
        if reset_time is None:
            reset_time = time.time() + 3600
        msg = ("Hit rate limit. Resets at %s" %
               datetime.datetime.fromtimestamp(reset_time).ctime())
        sleep_time = reset_time - time.time()
        self.logger.info(msg)
        if self.options.wait_for_rate_limit:
            self.logger.info("Sleeping %.2f seconds" % sleep_time)
            time.sleep(sleep_time)
            self.logger.info("Wait limit should be expired, resuming")
        else:
            raise StopScraping(msg)

    def parse_list(self, page):
        # NOrmally we'd get a string here, but it's easier
        # to do pagination if list_pages does its own parsing.
        results = page.get('results', [])
        for result in results:
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

        cleaned = {'title': text_from_html(record['name']),
                   'description': text_from_html(record.get('description', '')),
                   'location_name': location_name,
                   'location': Point(venue['lon'],
                                     venue['lat']),
                   'url': record['event_url'],
                   'item_date': event_time.date(),
                   }
        attributes = {'venue_phone': venue.get('phone', ''),
                      'venue_name': text_from_html(venue.get('name', '')),
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

    parser.add_option(
        '-p', '--start-page',
        help="Page of results to start from. Default is zero.",
        default=0
        )
    parser.add_option(
        "-n", "--no-wait-for-rate-limit",
        help="If we hit rate limit, exit instead of waiting until it resets (typically 1 hour). Default is to wait.",
        dest="wait_for_rate_limit", action='store_false', default=True,
        )
    options, args = parser.parse_args(argv)
    scraper = MeetupScraper(options)
    scraper.update()

if __name__ == '__main__':
    main()

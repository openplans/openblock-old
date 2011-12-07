#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

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
        """generate page ... well, not strings, but decoded JSON structures."""
        # TODO: This fetches a ton of data, which is maybe useful for
        # bootstrapping but very inefficient for getting updates.
        # For that we should support meetup's streaming API,
        # which allows passing a start time.

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
                zipcode = zipcode.slug
                zipcode_state.setdefault(zipcode, {'page': int(self.options.start_page),
                                                   'done': False})
                if zipcode_state[zipcode]['done']:
                    continue
                try:
                    int(zipcode)
                except ValueError:
                    # meetup will barf on these.
                    self.logger.info("Skipping %s, doesn't look like a valid US zip code" % zipcode)
                    continue

                params = dict(zip=zipcode, key=api_key, city=city, state=state,
                              country='US',
                              time='-1m,2m',
                              )
                pagenum = zipcode_state[zipcode]['page']
                self.logger.info("Page %s for zip code %s" % (pagenum, zipcode))
                params['offset'] = pagenum
                url = 'https://api.meetup.com/2/open_events?key=%(key)s&state=%(state)s&city=%(city)s&country=%(country)s&zip=%(zip)s&page=200&offset=%(offset)s' % params
                page, headers = self.retriever.fetch_data_and_headers(url,
                                                                      raise_on_error=False
)
                ratelimit_remaining = int(headers.get('x-ratelimit-remaining', '9999'))
                while ratelimit_remaining <= 1:
                    # Apparently meetup says you have 1 hit remaining
                    # when they actually mean "this is the last one."
                    # This either raises an exception, or eventually returns new data.
                    ratelimit_reset = int(headers.get('x-ratelimit-reset', 0))
                    page, headers = self.handle_ratelimit_exceeded(url, ratelimit_reset)
                    ratelimit_remaining = int(headers.get('x-ratelimit-remaining', 0))
                    break
                while int(headers.get('status')) >= 400:
                    try:
                        body = simplejson.loads(page)
                        problem, code = body.get('problem'), body.get('code')
                    except simplejson.JSONDecodeError:
                        problem = page
                        code = ''
                    if code == 'limit':
                        # This either raises an exception, or eventually returns new data.
                        page, headers = self.handle_ratelimit_exceeded(url)
                        break
                    else:
                        msg = "Error %s. %s: %s" % (headers.get('status'), code, problem)
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


    def handle_ratelimit_exceeded(self, url, reset_time=None):
        """
        Either sleep until rate limit expires, and retry the url;
        or raise StopScraping, depending on options.
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
        page, headers = self.retriever.fetch_data_and_headers(url, raise_on_error=False)
        return page, headers

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


from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
add_verbosity_options(parser)

def main(argv=None):
    import sys
    if argv is None:
        argv = sys.argv[1:]
    options, args = parser.parse_args(argv)
    scraper = MeetupScraper(options)
    setup_logging_from_opts(options, scraper.logger)
    scraper.update()

if __name__ == '__main__':
    main()

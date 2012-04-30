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


# NOTES BASED ON TEMPLATE:
# slug = 'photos'
# attributes:
#   photo_href = the 75x75 small square
#   username
#   user_id
#   sourcename  ... either 'Flickr' or 'Panoramio'


"""
An OpenBlock scraper for Flickr photos.

NOTE, to use this you must comply with the Flickr terms of service:
https://secure.flickr.com/services/api/tos/
"""

from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import simplejson
from ebdata.retrieval.scrapers.list_detail import StopScraping, SkipRecord
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebpub.db.models import NewsItem
from ebpub.geocoder.reverse import reverse_geocode, ReverseGeocodeError
from ebpub.utils.dates import parse_date
from ebpub.utils.geodjango import get_default_bounds
import datetime
import flickrapi
import logging
import pytz
import time

# Note there's an undocumented assumption in ebdata that we want to
# unescape html before putting it in the db.
from ebdata.retrieval.utils import convert_entities

local_tz = pytz.timezone(settings.TIME_ZONE)
utc = pytz.timezone('utc')

logger = logging.getLogger('eb.retrieval.flickr')

class FlickrScraper(NewsItemListDetailScraper):

    logname = 'flickr_retrieval'
    has_detail = False
    max_photos_per_scrape = 2000

    def __init__(self, options):
        self.api_key = settings.FLICKR_API_KEY
        self.api_secret = settings.FLICKR_API_SECRET
        self.options = options
        self.schema_slugs = [options.schema]
        self.records_seen = 0
        if options.end_date:
            end_date = parse_date(options.end_date, '%Y/%m/%d')
        else:
            end_date = datetime.date.today()
        # We want midnight at the *end* of the day.
        end_date += datetime.timedelta(days = 1)
        self.max_timestamp = time.mktime(end_date.timetuple())
        start_date = end_date - datetime.timedelta(days=options.days)
        self.min_timestamp = time.mktime(start_date.timetuple())


        super(FlickrScraper, self).__init__()

    def list_pages(self):
        """generate page strings."""

        # XXX argh we apparently need the api_secret, and thus the token / frob dance?
        # even though this method doesn't need authentication???
        flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret)
        extent = ','.join([str(coord) for coord in get_default_bounds().extent])

        # Result of each iteration is a JSON string.
        pagenum = 0
        pages = float('inf')
        while pagenum < pages:
            pagenum += 1
            page = flickr.photos_search(has_geo=1, bbox=extent, safe_search='1',
                                        min_taken_date=self.min_timestamp,
                                        max_taken_date=self.max_timestamp,
                                        per_page='400',
                                        page=str(pagenum),
                                        extras='date_taken,date_upload,url_sq,description,geo,owner_name',
                                        format='json',
                                        content_type='1', # photos only.
                                        nojsoncallback='1',
                                        )

            # Ugh, we need to find out how many pages there are, so we parse here
            # and also in parse_list().
            adict = simplejson.loads(page)
            try:
                pages = int(adict['photos']['pages'])
            except KeyError:
                if adict.get('stat') == 'fail':
                    self.logger.error("Flickr error code %r: %s" % (adict['code'], adict['message']))
                else:
                    self.logger.error("Page content:\n%s" %page)
                raise StopScraping("Parsing error, missing 'photos' or 'pages', see above.")
            yield page

    def parse_list(self, page):
        # parse a single detail string page into record dicts
        for photo in simplejson.loads(page)['photos']['photo']:
            if self.records_seen > self.max_photos_per_scrape:
                raise StopScraping("We've reached %d records" % self.max_photos_per_scrape)
            self.records_seen += 1
            yield photo

    def clean_list_record(self, record):
        # clean up a record dict
        # Item date, in timezone of the photo owner.
        # Not sure how to determine what that is, so we'll leave it.
        cleaned = {}
        cleaned['item_date'] = datetime.datetime.strptime(record['datetaken'],
                                                          '%Y-%m-%d %H:%M:%S')
        cleaned['item_date'] = cleaned['item_date'].date()
        # Posted date, UTC timestamp.
        pub_date = datetime.datetime.fromtimestamp(
            float(record['dateupload']), utc)
        cleaned['pub_date'] = pub_date.astimezone(local_tz)

        description = record['description']['_content']
        cleaned['description'] = convert_entities(description.strip())

        cleaned['title'] = convert_entities(record['title'])
        x, y = record['longitude'], record['latitude']
        cleaned['location'] = Point((float(x), float(y)))

        # Possibly we could figure out flickr's geo API and resolve
        # the photo's place_id and/or woeid to the place name?  But
        # those are probably not specific enough; reverse-geocode
        # instead.
        try:
            block, distance = reverse_geocode(cleaned['location'])
            cleaned['location_name'] = block.pretty_name
        except ReverseGeocodeError:
            raise SkipRecord("Could not geocode location %s, %s" % (x, y))

        # Don't think any of the urls returned by the API's "extras"
        # correspond to the page? not sure.
        cleaned['url'] = 'http://www.flickr.com/photos/%(owner)s/%(id)s' % record

        attributes = {}
        attributes['sourcename'] = 'Flickr'
        #attributes['photo_id'] = record['id']
        attributes['user_id'] = record['owner']
        attributes['username'] = record['ownername']
        # Thumbnail. 'Small square' photos are 75x75.
        attributes['photo_href'] = record['url_sq']
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
        '-d', "--days",
        help="How many days (prior to stop date) to search. Default is 30 days.",
        action='store', default=30, type='int',
        )
    parser.add_option(
        '-e', "--end-date",
        help="Stop date for photo search, format YYYY/MM/DD. Default is now.",
        action='store', default=None,
        )
    parser.add_option(
        "--schema", help="Slug of schema to use. Default is 'photos'.",
        action='store', default='photos',
        )

    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    add_verbosity_options(parser)

    options, args = parser.parse_args(argv)
    setup_logging_from_opts(options, logger)
    scraper = FlickrScraper(options)
    scraper.update()

if __name__ == '__main__':
    main()


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
from ebpub.utils.geodjango import get_default_bounds
import datetime
import flickrapi
import logging
import pytz
# Note there's an undocumented assumption in ebdata that we want to
# unescape html before putting it in the db.
from ebdata.retrieval.utils import convert_entities

local_tz = pytz.timezone(settings.TIME_ZONE)
utc = pytz.timezone('utc')
logger = logging.getLogger()

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
                                        min_taken_date=None, #XXX unix timestamp
                                        max_taken_date=None, #XXX timestamp
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
            pages = int(adict['photos']['pages'])
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
        "--start-date", help="Start date for photo search. Default is 30 days ago.",
        action='store', default=None,
        )
    parser.add_option(
        "--end-date", help="Stop date for photo search. Default is now",
        action='store', default=None,
        )
    parser.add_option(
        "--schema", help="Slug of schema to use. Default is 'photos'.",
        action='store', default='photos',
        )

    options, args = parser.parse_args(argv)
    scraper = FlickrScraper(options)
    scraper.update()

if __name__ == '__main__':
    main()

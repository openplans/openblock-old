
# NOTES BASED ON TEMPLATE:
# slug = 'photos'
# attributes:
#   photo_href = the 75x75 small square
#   username
#   user_id
#   source.name  ... either 'Flickr' or 'Panoramio'


"""
An OpenBlock scraper for Flickr photos.

NOTE, to use this you must comply with the Flickr terms of service:
https://secure.flickr.com/services/api/tos/
"""

from django.conf import settings
from django.contrib.gis.geos import Point
from ebpub.db.models import NewsItem, Schema, Lookup
from ebpub.utils.geodjango import get_default_bounds
import flickrapi
import logging
import datetime
import pytz
# Note there's an undocumented assumption in ebdata that we want to
# unescape html before putting it in the db.
from ebdata.retrieval.utils import convert_entities

local_tz = pytz.timezone(settings.TIME_ZONE)
utc = pytz.timezone('utc')
logger = logging.getLogger()


class FlickrScraper(object):
    def __init__(self, options):
        self.api_key = settings.FLICKR_API_KEY
        self.api_secret = settings.FLICKR_API_SECRET
        self.options = options

    def update(self):
        # XXX argh we apparently need the api_secret, and thus the token / frob dance?
        # even though this method doesn't need authentication???
        options = self.options

        flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret)
        extent = ','.join([str(coord) for coord in get_default_bounds().extent])

        # Result XML is parsed to an ElementTree node.
        rsp = flickr.photos_search(has_geo=1, bbox=extent, safe_search='1',
                                   min_taken_date=None, #XXX unix timestamp
                                   max_taken_date=None, #XXX timestamp
                                   per_page='10', # XXX
                                   extras='date_taken,date_upload,url_sq,description,geo',
                                   )
        try:
            schema = Schema.objects.get(slug=options.schema)
        except Schema.DoesNotExist:
            logger.error( "Schema (%s): DoesNotExist" % self.schema_slug)
            return 1

        for photo in rsp.find('photos'):
            # Don't think any of the urls returned by the API's "extras"
            # correspond to the page? not sure.
            url = 'http://www.flickr.com/photos/%(owner)s/%(id)s' % photo.attrib
            try:
                item = NewsItem.objects.get(schema=schema, url=url)
                logger.info(" skip existing photo %s" % url)
                continue
            except NewsItem.DoesNotExist:
                logger.info("Creating photo from %s" % url)
                item = NewsItem(schema=schema, url=url)

            # Item date, in timezone of the photo owner.
            # Not sure how to determine what that is, so we'll leave it.
            item.item_date = datetime.datetime.strptime(photo.attrib['datetaken'],
                                                        '%Y-%m-%d %H:%M:%S')
            # Posted date, UTC timestamp.
            pub_date = datetime.datetime.fromtimestamp(
                float(photo.attrib['dateupload']), utc)
            item.pub_date = pub_date.astimezone(local_tz)

            description = photo.get('description') and photo.get('description').text or ''
            item.description = convert_entities(description.strip())
            item.title = convert_entities(photo.attrib['title'])
            x, y = photo.attrib['longitude'], photo.attrib['latitude']
            item.location = Point((float(x), float(y)))

            # TODO: we could figure out flickr's geo API and
            # resolve the photo's place_id and/or woeid to the place name?
            # No, those are probably not specific enough; reverse-geocode instead.
            item.location_name = 'XXX'

            item.save()

            item.attributes['source.name'] = 'Flickr'
            #item.attributes['photo_id'] = photo.attrib['id']
            item.attributes['user_id'] = photo.attrib['owner']
            # Thumbnail. 'Small square' photos are 75x75.
            item.attributes['photo_href'] = photo.attrib['url_sq']
            item.save()


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

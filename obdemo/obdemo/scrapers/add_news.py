#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#


"""A quick-hack news scraper script for Boston; consumes RSS feeds.
"""

import datetime
import feedparser
import logging
import sys

from django.contrib.gis.geos import Point
from ebdata.nlp.addresses import parse_addresses
from ebpub.db.models import NewsItem, Schema
from ebpub.geocoder import SmartGeocoder
from ebpub.geocoder.base import GeocodingException
from ebpub.utils.logutils import log_exception

# Note there's an undocumented assumption in ebdata that we want to
# unescape html before putting it in the db.
from ebdata.retrieval.utils import convert_entities

logger = logging.getLogger('add_news')

def update(argv=None):
    logger.info("Starting add_news")
    if argv:
        url = argv[0]
    else:
        url = 'http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&subject=massachusetts&scope=bonzai'
    schema_slug = 'local-news'

    try:
        schema = Schema.objects.get(slug=schema_slug)
    except Schema.DoesNotExist:
        logger.error( "Schema (%s): DoesNotExist" % schema_slug)
        sys.exit(1)

    f = feedparser.parse(url)
    addcount = updatecount = 0
    for entry in f.entries:
        title = convert_entities(entry.title)
        description = convert_entities(entry.description)

        if entry.id.startswith('http'):
            item_url = entry.id
        else:
            item_url = entry.link
        try:
            item = NewsItem.objects.get(schema__id=schema.id,
                                        title=title,
                                        description=description)
            #url=item_url)
            status = 'updated'
        except NewsItem.DoesNotExist:
            item = NewsItem()
            status = 'added'
        except NewsItem.MultipleObjectsReturned:
            # Seen some where we get the same story with multiple URLs. Why?
            logger.warn("Multiple entries matched title %r and description %r. Expected unique!" % (title, description))
            continue
        try:
            item.title = title
            item.schema = schema
            item.description = description
            item.url = item_url
            item.location_name = entry.get('x-calconnect-street') or entry.get('georss_featurename')
            item.item_date = datetime.datetime(*entry.updated_parsed[:6])
            item.pub_date = datetime.datetime(*entry.updated_parsed[:6])

            # feedparser bug: depending on which parser it magically uses,
            # we either get the xml namespace in the key name, or we don't.
            point = entry.get('georss_point') or entry.get('point')
            x, y = None, None
            if point:
                x, y = point.split(' ')
            if True:
                # Fall back on geocoding.
                text = item.title + ' ' + item.description
                addrs = parse_addresses(text)
                for addr, unused in addrs:
                    try:
                        result = SmartGeocoder().geocode(addr)
                        point = result['point']
                        logger.debug("internally geocoded %r" % addr)
                        x, y = point.x, point.y
                        break
                    except GeocodingException:
                        logger.debug("Geocoding exception on %r:" % text)
                        log_exception(level=logging.DEBUG)
                        continue
                    except:
                        logger.error('uncaught geocoder exception on %r\n' % addr)
                        log_exception()
                if None in (x, y):
                    logger.info("couldn't geocode '%s...'" % item.title[:30])
                    continue
            item.location = Point((float(y), float(x)))
            if item.location.x == 0.0 and item.location.y == 0.0:
                # There's a lot of these. Maybe attempt to
                # parse and geocode if we haven't already?
                logger.info("Skipping %r as it has bad location 0,0" % item.title)
                continue
            if not item.location_name:
                # Fall back to reverse-geocoding.
                from ebpub.geocoder import reverse
                try:
                    block, distance = reverse.reverse_geocode(item.location)
                    logger.debug(" Reverse-geocoded point to %r" % block.pretty_name)
                    item.location_name = block.pretty_name
                    item.block = block
                except reverse.ReverseGeocodeError:
                    logger.debug(" Failed to reverse geocode %s for %r" % (item.location.wkt, item.title))
                    item.location_name = u''
            item.save()
            if status == 'added':
                addcount += 1
            else:
                updatecount += 1
            logger.info("%s: %s" % (status, item.title))
        except:
            logger.error("Warning: couldn't save %r. Traceback:" % item.title)
            log_exception()
    logger.info("Finished add_news: %d added, %d updated" % (addcount, updatecount))

def main(argv=None):
    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    from optparse import OptionParser
    if argv is None:
        argv = sys.argv[1:]
    optparser = OptionParser()
    add_verbosity_options(optparser)
    opts, args = optparser.parse_args(argv)
    setup_logging_from_opts(opts, logger)
    update(args)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

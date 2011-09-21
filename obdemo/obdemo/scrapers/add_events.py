#!/usr/bin/env python
# encoding: utf-8

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

#pylint: disable-msg=E1101
#pylint: disable-msg=W0142

"""
add_events.py

Created by Don Kukral <don_at_kukral_dot_org>

Downloads calendar entries from RSS feed at boston.com 
and updates the database
"""

import sys, feedparser, datetime
import logging

from django.contrib.gis.geos import Point
from ebpub.db.models import NewsItem, Schema
from ebpub.utils.logutils import log_exception

logger = logging.getLogger('add_events')

# Note there's an undocumented assumption in ebdata that we want to
# put unescape html before putting it in the db.  Maybe wouldn't have
# to do this if we used the scraper framework in ebdata?
from ebdata.retrieval.utils import convert_entities


def update():
    """ Download Calendar RSS feed and update database """
    logger.info("Starting add_events")
    url = """http://calendar.boston.com/search?acat=&cat=&commit=Search\
&new=n&rss=1&search=true&sort=0&srad=20&srss=50&ssrss=5&st=event\
&st_select=any&svt=text&swhat=&swhen=today&swhere=&trim=1"""
    schema = 'events'


    try:
        schema = Schema.objects.get(slug=schema)
    except Schema.DoesNotExist:
        logger.error("Schema (%s): DoesNotExist" % schema)
        sys.exit(1)

    feed = feedparser.parse(url)
    addcount = updatecount = 0
    for entry in feed.entries:
        title = convert_entities(entry.title)
        try:
            item = NewsItem.objects.get(title=title,
                                        schema__id=schema.id)
            status = "updated"
        except NewsItem.DoesNotExist:
            item = NewsItem()
            status = "added"
        except NewsItem.MultipleObjectsReturned:
            logger.warn("Multiple entries matched title %r, event titles are not unique?" % title)
            continue
        try:
            item.location_name = entry.get('xcal_x-calconnect-street') or entry.get('x-calconnect-street') or u''
            item.schema = schema
            item.title = title
            item.description = convert_entities(entry.description)
            item.url = entry.link
            item.item_date = datetime.datetime(*entry.updated_parsed[:6])
            item.pub_date = datetime.datetime(*entry.updated_parsed[:6])
            item.location = Point((float(entry['geo_long']),
                                   float(entry['geo_lat'])))
            if (item.location.x, item.location.y) == (0.0, 0.0):
                logger.warn("Skipping %r, bad location 0,0" % item.title)
                continue

            if not item.location_name:
                # Fall back to reverse-geocoding.
                from ebpub.geocoder import reverse
                try:
                    block, distance = reverse.reverse_geocode(item.location)
                    logger.info(" Reverse-geocoded point to %r" % block.pretty_name)
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
            logger.error("unexpected error:", sys.exc_info()[1])
            log_exception()
    logger.info("add_events finished: %d added, %d updated" % (addcount, updatecount))



def main(argv=None):
    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    from optparse import OptionParser
    if argv is None:
        argv = sys.argv[1:]
    optparser = OptionParser()
    add_verbosity_options(optparser)
    opts, args = optparser.parse_args(argv)
    setup_logging_from_opts(opts, logger)
    update()

if __name__ == '__main__':
    sys.exit(main())


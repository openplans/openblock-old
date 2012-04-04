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

from django.conf import settings
from django.contrib.gis.geos import Point
from ebpub.db.models import NewsItem, Schema
from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
from optparse import OptionParser
import dateutil.parser
import ebdata.retrieval.log  # sets up base handlers.
import logging
import pytz
import sys, feedparser, datetime

# Note there's an undocumented assumption in ebdata that we want to
# put unescape html before putting it in the db.  Maybe wouldn't have
# to do this if we used the scraper framework in ebdata?
from ebdata.retrieval.utils import convert_entities

logger = logging.getLogger('eb.retrieval.boston.events')

local_tz = pytz.timezone(settings.TIME_ZONE)

class EventsCalendarScraper(object):

    url = "http://calendar.boston.com/search?commit=Search&new=n&rss=1&search=true&srad=50&srss=&st=event&st_select=event&svt=text&swhat=&swhen=&swhere="

    def __init__(self, schema_slug='events'):
        try:
            self.schema = Schema.objects.get(slug=schema_slug)
        except Schema.DoesNotExist:
            logger.error("Schema (%s): DoesNotExist" % schema_slug)
            sys.exit(1)
        
    def update(self):
        """ Download Calendar RSS feed and update database """
        logger.info("Starting EventsCalendarScraper")
        
        feed = feedparser.parse(self.url)
        seencount = addcount = updatecount = 0
        for entry in feed.entries:

            def ns_get(element):
                # work around feedparser unpredictability.
                namespace, element = element.split(':')
                result = entry.get('%s_%s' % (namespace, element))
                if result is None:
                    result = entry.get(element)
                return result

            seencount += 1
            title = convert_entities(entry.title)
            try:
                item = NewsItem.objects.get(title=title,
                                            schema__id=self.schema.id)
                status = "updated"
            except NewsItem.DoesNotExist:
                item = NewsItem()
                status = "added"
            except NewsItem.MultipleObjectsReturned:
                logger.warn("Multiple entries matched title %r, event titles are not unique?" % title)
                continue
            try:
                item.location_name = '%s %s' % (ns_get('xcal:x-calconnect-venue-name'),
                                                ns_get('xcal:x-calconnect-street'))
                item.location_name = item.location_name.strip()
                item.schema = self.schema
                item.title = title
                item.description = convert_entities(entry.description)
                item.url = entry.link
                start_dt = ns_get('xcal:dtstart')
                start_dt = dateutil.parser.parse(start_dt)
                # Upstream bug: They provide a UTC offset of +0000 which
                # means times in UTC, but they're actually times in
                # US/Eastern, so do *not* fix the zone.
                #start_dt = start_dt.astimezone(local_tz)
                item.item_date = start_dt.date()
                item.pub_date = datetime.datetime(*entry.updated_parsed[:6])
                item.location = Point((float(ns_get('geo:long')),
                                       float(ns_get('geo:lat'))))
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
                    except reverse.ReverseGeocodeError:
                        logger.debug(" Failed to reverse geocode %s for %r" % (item.location.wkt, item.title))
                        item.location_name = u''

                item.save()
                item.attributes['start_time'] = start_dt.time()
                end_dt = ns_get('xcal:dtend') or u''
                if end_dt.strip():
                    end_dt = dateutil.parser.parse(end_dt.strip())
                    #end_dt = end_dt.astimezone(local_tz)
                    item.attributes['end_time'] = end_dt.time()
                if status == 'added':
                    addcount += 1
                else:
                    updatecount += 1
                logger.info("%s: %s" % (status, item.title))
            except Exception as e:
                logger.exception("unexpected error: %s" % e)
        logger.info("EventsCalendarScraper finished: %d added, %d updated of %s total" % (addcount, updatecount, seencount))

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    optparser = OptionParser()
    add_verbosity_options(optparser)
    opts, args = optparser.parse_args(argv)
    setup_logging_from_opts(opts, logger)
    EventsCalendarScraper().update()

if __name__ == '__main__':
    sys.exit(main())

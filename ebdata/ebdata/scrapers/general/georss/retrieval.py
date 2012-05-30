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


"""A scraper for RSS feeds with GeoRSS or other location info.
"""

import datetime
import ebdata.retrieval.log  # sets up base handlers.

from django.contrib.gis.geos import Point
from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
from ebdata.retrieval.scrapers.list_detail import SkipRecord, StopScraping
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebpub.db.models import NewsItem
from ebpub.utils.geodjango import intersects_metro_bbox


# Note there's an undocumented assumption in ebdata that we want to
# unescape html before putting it in the db.
from ebdata.retrieval.utils import convert_entities

class RssScraper(RssListDetailScraper, NewsItemListDetailScraper):
    """
    A generic RSS scraper. Suitable for use with any Schema that
    doesn't have any associated SchemaFields (that is, no extended
    attributes, just the core NewsItem stuff.)
    """

    has_detail = False
    logname = 'georss'

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url', None)
        self.schema_slugs = (kwargs.pop('schema_slug', None) or 'local-news',)
        super(RssScraper, self).__init__(*args, **kwargs)

    def list_pages(self):
        result = self.fetch_data(self.url)
        if self.retriever.cache_hit:
            self.logger.info("HTTP cache hit, nothing new to do")
            raise StopScraping()
        yield result

    def existing_record(self, record):
        url = record.get('id', '') or record.link
        qs = list(NewsItem.objects.filter(schema__id=self.schema.id, url=url))
        if not qs:
            return None

        if len(qs) > 1:
            self.logger.warn("Multiple entries matched url %r and schema %r. Expected unique! Using first one." % (url, qs[0].schema.slug))
        return qs[0]

    def clean_list_record(self, record):
        record.title = convert_entities(record['title'])
        record.description = convert_entities(record['description'])
        # Don't know why, but some feeds have 'id' *instead* of 'link'.
        if record.get('id', '').startswith('http'):
            record['link'] = record['id']

        # This tries GeoRSS, RDF Geo, xCal, ...
        point, location_name = self.get_point_and_location_name(record)

        _short_title = record['title'][:30] + '...'

        if not point:
            raise SkipRecord("couldn't geocode any addresses in item '%s...'"
                             % _short_title)

        if not location_name:
            raise SkipRecord(
                "Skip, no location name and failed to reverse geocode %s for %r" % (point.wkt, _short_title))

        if not intersects_metro_bbox(point):
            # Check if latitude, longitude seem to be reversed; I've
            # seen that in some bad feeds!
            reversed_loc = Point(point.y, point.x)
            if intersects_metro_bbox(reversed_loc):
                self.logger.info(
                    "Got points in apparently reverse order, flipping them")
                point = reversed_loc
            else:
                raise SkipRecord("Skipping %r as %s,%s is out of bounds" %
                                 (_short_title, point.y, point.x))

        record['location_name'] = location_name
        record['location'] = point
        return record


    def update(self, *args, **kwargs):
        self.logger.info("Retrieving %s" % self.url)
        result = super(RssScraper, self).update(*args, **kwargs)
        self.logger.info("Added: %d; Updated: %d; Skipped: %d" %
                         (self.num_added, self.num_changed, self.num_skipped))
        return result


    def save(self, old_record, list_record, detail_record):
        item_date = datetime.datetime(*list_record.updated_parsed[:6])
        pub_date = item_date

        kwargs = dict(location_name=list_record['location_name'],
                      location=list_record['location'],
                      item_date=item_date,
                      pub_date=pub_date,
                      title=list_record['title'],
                      description=list_record['description'],
                      url=list_record['link'],
                      )
        attributes = None
        self.create_or_update(old_record, attributes, **kwargs)


def main(argv=None, default_url=None):
    import sys
    if argv is None:
        argv = sys.argv[1:]

    from optparse import OptionParser
    usage = "usage: %prog [options] <feed url>"
    parser = OptionParser(usage=usage)

    parser.add_option(
        "--schema", help="Slug of the news item type to create when scraping",
        default="local-news"
        )
    # parser.add_option(
    #     "--http-cache", help='location to use as an http cache.  If a cached value is seen, no update is performed.', 
    #     action='store'
    #     )

    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    add_verbosity_options(parser)

    options, args = parser.parse_args(argv)
    if len(args) >= 1:
        url = args[0]
    else:
        if default_url:
            url = default_url
        else:
            parser.print_usage()
            sys.exit(0)

    scraper = RssScraper(url=url, schema_slug=options.schema)
    setup_logging_from_opts(options, scraper.logger)
    scraper.update()

if __name__ == '__main__':
    main()

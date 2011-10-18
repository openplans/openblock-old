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

from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
from ebdata.retrieval.scrapers.list_detail import SkipRecord
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebpub.db.models import NewsItem

import datetime
import math

#BASE_URL = 'https://seeclickfix.com/api/'
# This one is load-balanced, as requested by the SeeClickFix guys.
BASE_URL = 'http://seeclicktest.com/api/'


class SeeClickFixNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):
    """
    For all of these methods, see docstrings in
    ebdata.retrieval.scrapers.list_detail.ListDetailScraper
    """

    schema_slugs = ('issues',)
    has_detail = True
    logname = 'seeclickfix'
    sleep = 2

    def __init__(self, *args, **kwargs):
        self.city = kwargs.pop('city', None)
        if self.city:
            self.city = self.city.replace(' ', '+')
        self.state = kwargs.pop('state', None)
        super(SeeClickFixNewsFeedScraper, self).__init__(*args, **kwargs)

    def list_pages(self):
        # Fetch the feed, paginating if necessary.
        # See API docs at http://help.seeclickfix.com/faqs/api/listing-issues
        max_per_page = 500
        max_pages = 4
        url = BASE_URL + 'issues.rss?sort=issues.created_at&direction=DESC'
        if self.city and self.state:
            url = '%s&at=%s,+%s' %  (url, self.city, self.state)

        # First, figure out how long it's been since the last scrape;
        # seeclickfix has a 'start' option in hours.  The idea is not
        # to be precise, but to get everything we haven't seen yet and
        # not much that we have seen. So we'll discard microseconds
        # and round up.
        delta = datetime.datetime.now() - self.last_updated_time()
        hours_ago = math.ceil((delta.seconds / 3600.0) + (delta.days * 24))
        for page in range(1, max_pages + 1):
            feed_url = url + '&start=%d&page=%d&num_results=%d' % (
                hours_ago, page, max_per_page)
            self.logger.info("Fetching %s" % feed_url)
            yield self.fetch_data(feed_url)

    def existing_record(self, cleaned_list_record):
        url = cleaned_list_record['id'].replace('http://seeclicktest.com/', 'http://seeclickfix.com/')
        qs = NewsItem.objects.filter(schema__id=self.schema.id, url=url)
        try:
            return qs[0]
        except IndexError:
            return None

    def detail_required(self, list_record, old_record):
        # Always fetch detail pages.
        return True

    def get_detail(self, record):
        # There's no direct link to the JSON detail page,
        # but we can construct one by munging the GUID link.
        url = record['guid'].replace('.html', '.json')
        return self.fetch_data(url)

    def parse_detail(self, page, list_record):
        from django.utils import simplejson
        return simplejson.loads(page)[0]

    def get_location(self, record):
        from django.contrib.gis.geos import Point
        lon = record['lng']
        lat = record['lat']
        return Point(lon, lat)

    def clean_detail_record(self, record):
        location = self.get_location(record)
        # TODO: try self.safe_location? see newsitem_list_detail

        # This is a common error in some data sources we've seen...
        if location and (location.x == 0.0 and location.y == 0.0):
            self.logger.warn("skipping %r as it has bad location 0,0" % record['summary'])
            raise SkipRecord

        item_date = datetime.datetime.strptime(record['created_at'],
                                               '%m/%d/%Y at %I:%M%p')
        item_date = item_date.date()

        url = 'http://seeclickfix.com/issues/%d.html' % record['issue_id']
        attributes = {'rating': record['rating'],
                      }

        result = dict(title=record['summary'],
                      description=record['description'] or u'',
                      item_date=item_date,
                      location=location,
                      location_name=record['address'] or u'', # maybe fall back to reverse-geocoding? Maybe the framework should do that?
                      url=url,
                      attributes=attributes,
                      )
        return result

    def save(self, old_record, list_record, detail_record):
        attributes = detail_record.pop('attributes', None)
        self.create_or_update(old_record, attributes, **detail_record)


def main(argv=None):
    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    import ebdata.retrieval.log # Sets up standard handlers.
    import sys
    if argv is None:
        argv = sys.argv[1:]

    from optparse import OptionParser
    usage = "usage: %prog [options] city state"
    parser = OptionParser(usage=usage)
    add_verbosity_options(parser)

    options, args = parser.parse_args(argv)
    if len(args) != 2:
        parser.print_usage()
        sys.exit(0)
    city, state = args
    scraper = SeeClickFixNewsFeedScraper(city=city.title(), state=state.upper())
    setup_logging_from_opts(options, scraper.logger)

    TESTING = False
    if TESTING:
        from ebdata.retrieval import log_debug
        scraper.display_data()
    else:
        scraper.update()

if __name__ == "__main__":
    main()

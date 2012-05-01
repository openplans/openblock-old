#   Copyright 2011,2012 OpenPlans and contributors
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

"""

Boston police reports scraper.
http://www.bpdnews.com/

"""

from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
from ebdata.retrieval.scrapers.list_detail import SkipRecord
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.textmining.treeutils import text_from_html
from ebpub.db.models import NewsItem
import datetime


class BPDNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):

    schema_slugs = ('police-reports',)
    has_detail = False
    logname = 'boston.police_reports'

    # Can't find a way to specify number of items.
    url = 'http://www.bpdnews.com/feed/'

    def list_pages(self):
        yield self.fetch_data(self.url)

    def existing_record(self, cleaned_record):
        url = cleaned_record['url']
        qs = NewsItem.objects.filter(schema__id=self.schema.id, url=url)
        try:
            return qs[0]
        except IndexError:
            return None

    def clean_list_record(self, record):
        if record['title'].startswith(u'Boston 24'):
            # We don't include the summary posts.
            # TODO: the 'Boston 24' tag indicates posts with aggregate
            # daily stats.  Make a separate schema for the aggregates,
            # with attributes like those used in
            # everyblock/everyblock/cities/nyc/crime_aggregate/retrieval.py.
            # Or maybe not: these are citywide, not by precinct.
            # So what would be the Location?  Whole city??
            self.logger.info("boston daily crime stats, we don't know how to "
                             "handle these yet")
            raise SkipRecord

        date = datetime.date(*record['updated_parsed'][:3])
        description = record['summary']

        # This feed doesn't provide geographic data; we'll try to
        # extract addresses from the text, and stop on the first
        # one that successfully geocodes.
        full_description = record['content'][0]['value']
        full_description = text_from_html(full_description)
        location, location_name = self.get_point_and_location_name(
            record, address_text=full_description)

        if not (location or location_name):
            raise SkipRecord("No location or location_name")

        # Get the precinct from the tags.
        precincts = ['A1', 'A15', 'A7', 'B2', 'B3', 'C11', 'C6', 'D14', 'D4',
                     'E13', 'E18', 'E5']
        tags = [t['term'] for t in record['tags']]
        precinct = None
        for tag in tags:
            if tag in precincts:
                # TODO: we need a LocationType for precincts, and shapes; and
                # then we could set newsitem.location_object to the Location
                # for this precinct. For now we just save it as an attribute.
                precinct = tag
                break

        attributes = {}
        if precinct:
            precinct = self.get_or_create_lookup('precinct', precinct, precinct)
            attributes['precinct'] = precinct.id
        else:
            raise SkipRecord("no precinct found in tags %r" % tags)

        cleaned = dict(item_date=date,
                       location=location,
                       location_name=location_name,
                       title=record['title'],
                       description=description,
                       url=record['link'],
                       attributes=attributes,
                       )

        return cleaned


    def save(self, old_record, list_record, detail_record):
        attributes = list_record.pop('attributes', None)
        # We don't use detail_record
        kwargs = list_record
        self.create_or_update(old_record, attributes, **kwargs)


def main(argv=None):
    import sys
    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    from optparse import OptionParser
    if argv is None:
        argv = sys.argv[1:]
    optparser = OptionParser()
    add_verbosity_options(optparser)
    scraper = BPDNewsFeedScraper()
    opts, args = optparser.parse_args(argv)
    setup_logging_from_opts(opts, scraper.logger)
    scraper.update()

if __name__ == "__main__":
    main()

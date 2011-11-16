#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of everyblock
#
#   everyblock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   everyblock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with everyblock.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Screen scraper for Boston restaurant inspections.

http://www.cityofboston.gov/isd/health/mfc/search.asp
"""

from django.core.serializers.json import DjangoJSONEncoder
from ebdata.retrieval.scrapers.base import ScraperBroken
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebpub.db.models import NewsItem
from ebpub.utils.dates import parse_date
from ebpub.utils.text import smart_title
import re

parse_main_re = re.compile(r"<tr[^>]*><td[^>]*><a href='insphistory\.asp\?licno=(?P<restaurant_id>\d+)'>(?P<restaurant_name>[^<]*)</a></td><td[^>]*>(?P<address>[^<]*)</td><td[^>]*>(?P<neighborhood>[^<]*)</td></tr>")
detail_violations_re = re.compile(r"<tr[^>]*><td[^>]*><span[^>]*>(?P<stars>\*+)</span></td><td[^>]*><span[^>]*>(?P<status>[^<]*)</span></td><td[^>]*><span[^>]*>(?P<code>[^<]*)</span></td><td[^>]*><span[^>]*>(?P<description>[^<]*)<p><i>Comments:<br></i>(?P<comment>[^<]*)</p></span></td><td[^>]*><span[^>]*>(?P<location>.*?)</span></td></tr>", re.DOTALL)
detail_url = lambda inspection_id: 'http://www.cityofboston.gov/isd/health/mfc/viewinsp.asp?inspno=%s' % inspection_id

strip_tags = lambda x: re.sub(r'(?s)</?[^>]*>', '', x).replace('&nbsp;', ' ').strip()

class RestaurantScraper(NewsItemListDetailScraper):

    logname = 'us.ma.boston.restaurants'

    # Sadly, there appears to be no way to query by date;
    # we have no choice but to crawl the entire site every time.

    schema_slugs = ('restaurant-inspections',)
    detail_address_re = re.compile(r"View Inspections[^<]*</div>[^<]*<br/?>?<b>(?P<restaurant_name>[^<]*)</b>[^<]*<br/>(?P<address_1>[^<]*)<br/>(?P<address_2>[^<]*)(?P<zipcode>\d\d\d\d\d)[^<]*<br/>")
    parse_list_re = re.compile(r" href='viewinsp\.asp\?inspno=(?P<inspection_id>\d+)'>(?P<inspection_date>[^<]*)</a></span></td><td[^>]*><span[^>]*>(?P<result>[^<]*)</span>")
    parse_detail_re = re.compile(r"<th[^>]*>Status</th><th[^>]*>Code Violation</th><th[^>]*>Description</th><th[^>]*>Location</th></tr>(?P<body>.*?)</table>", re.DOTALL)
    sleep = 4

    def __init__(self, name_start=''):
        # name_start, if given, should be a string of the first restaurant name
        # to start scraping, alphabetically. This is useful if you've run the
        # scraper and it's broken several hours into it -- you can pick up
        # around where it left off.
        NewsItemListDetailScraper.__init__(self)
        self.name_start = (name_start or u'').lower().strip()


    def update(self, *args, **kwargs):
        self.logger.info("This is a VERY slow scraper, it typically takes hours!")
        import time
        start = time.time()
        super(RestaurantScraper, self).update(*args, **kwargs)
        elapsed = time.time() - start
        hours, elapsed = divmod(elapsed, 3600)
        mins, secs = divmod(elapsed, 60)
        self.logger.info("Done scraping restaurants in %02d:%02d:%02d" % (hours, mins, secs))
        
    def list_pages(self):
        # Submit the search form with ' ' as the neighborhood to get *every*
        # restaurant in the city.
        #
        # Note that this site is technically *three* levels deep -- there's a
        # main list of all restaurants, then a list of inspections for each
        # restaurant, then a page for each inspection. Because this is slightly
        # different than a strict list-detail site, list_pages() yields the
        # inspection pages, not the main page.
        url = 'http://www.cityofboston.gov/isd/health/mfc/search.asp'
        html = self.get_html(url, {'ispostback': 'true', 'restname': '', 'cboNhood': ' '}).decode('ISO-8859-2')
        for record in parse_main_re.finditer(html):
            record = record.groupdict()
            if self.name_start and record['restaurant_name'].lower() < self.name_start:
                self.logger.info('Skipping %r due to name_start %r', record['restaurant_name'], self.name_start)
                continue
            self.logger.info('Getting inspections for %s' % record['restaurant_name'])
            url = 'http://www.cityofboston.gov/isd/health/mfc/insphistory.asp?licno=%s' % record['restaurant_id']
            # Normally we'd just yield the html, but we want the
            # record dict for use in parse_list().
            yield (record, self.get_html(url))

    def parse_list(self, record_html):
        # Normally this method gets passed raw html,
        # but we return both the html and the list_record from list_pages().
        list_record, html = record_html
        # a better version of the restaurant address is available on this page,
        # attempt to extract additional location details to resolve ambiguities.
        try:
            info = self.detail_address_re.search(html).groupdict()
            list_record['zipcode'] = info['zipcode']
        except:
            self.logger.info("Could not get detailed address information for record %s: %s" % (list_record['restaurant_id'], list_record['restaurant_name']))

        for record in NewsItemListDetailScraper.parse_list(self, html):
            yield dict(list_record, **record)

    def clean_list_record(self, record):
        record['inspection_date'] = parse_date(record['inspection_date'], '%m/%d/%Y')
        record['address'] = smart_title(record['address'])
        record['restaurant_name'] = smart_title(record['restaurant_name'])
        record['result'] = smart_title(record['result'])
        return record

    def existing_record(self, record):
        try:
            qs = NewsItem.objects.filter(schema__id=self.schema.id)
            qs = qs.by_attribute(self.schema_fields['inspection_id'], record['inspection_id'])
            return qs[0]
        except IndexError:
            return None

    def detail_required(self, list_record, old_record):
        return old_record is None

    def get_detail(self, record):
        return self.get_html(detail_url(record['inspection_id'])).decode('ISO-8859-2')

    def clean_detail_record(self, record):
        body = record.pop('body')
        violations = [m.groupdict() for m in detail_violations_re.finditer(body)]
        if not violations and not 'There are no violations for this inspection' in body:
            raise ScraperBroken('Could not find violations')
        for vio in violations:
            vio['severity'] = {1: 'Non critical', 2: 'Critical', 3: 'Critical foodborne illness'}[vio.pop('stars').count('*')]
            vio['comment'] = strip_tags(vio['comment']).strip()
            vio['location'] = strip_tags(vio['location']).strip()
            vio['description'] = strip_tags(vio['description']).strip()
            vio['status'] = strip_tags(vio['status']).strip()
        record['violation_list'] = violations
        return record

    def save(self, old_record, list_record, detail_record):
        if old_record is not None:
            return # We already have this inspection.

        result = self.get_or_create_lookup('result', list_record['result'], list_record['result'])
        violation_lookups = [self.get_or_create_lookup('violation', v['description'], v['code'], make_text_slug=False) for v in detail_record['violation_list']]

        violation_lookup_text = ','.join([str(v.id) for v in violation_lookups])
        if len(violation_lookup_text) > 4096:
            # This is an ugly hack to work around the fact that
            # many-to-many Lookups are themselves an ugly hack.
            # See http://developer.openblockproject.org/ticket/143
            violation_lookup_text = violation_lookup_text[0:4096]
            violation_lookup_text = violation_lookup_text[0:violation_lookup_text.rindex(',')]
            self.logger.warning('Restaurant %r had too many violations to store, skipping some!', list_record['restaurant_name'])

        # There's a bunch of data about every particular violation, and we
        # store it as a JSON object. Here, we create the JSON object.
        v_lookup_dict = dict([(v.code, v) for v in violation_lookups])
        v_list = [{'lookup_id': v_lookup_dict[v['code']].id, 'comment': v['comment'], 'location': v['location'], 'severity': v['severity'], 'status': v['status']} for v in detail_record['violation_list']]
        violations_json = DjangoJSONEncoder().encode(v_list)

        title = '%s inspected: %s' % (list_record['restaurant_name'], result.name)
        attributes = {
            'restaurant_id': list_record['restaurant_id'],
            'inspection_id': list_record['inspection_id'],
            'restaurant_name': list_record['restaurant_name'],
            'result': result.id,
            'violation': violation_lookup_text,
            'details': violations_json,
        }
        try: 
            self.create_newsitem(
                attributes,
                title=title,
                url=detail_url(list_record['inspection_id']),
                item_date=list_record['inspection_date'],
                location_name=list_record['address'],
                zipcode=list_record.get('zipcode')
            )
        except:
            import traceback;
            self.logger.error("Error storing inspection for %s: %s" % (list_record.get('restaurant_name', 'Unknown'), traceback.format_exc())) 


def main(argv=None):
    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    import sys
    if argv is None:
        argv = sys.argv[1:]
    from optparse import OptionParser
    parser = OptionParser()
    add_verbosity_options(parser)
    parser.add_option('-n', '--name-start', help='Name of first restaurant to start with.'
                      ' This is useful if you\'ve run the scraper and it\'s broken '
                      'several hours into it; you can pick up around where it left off.')

    options, args = parser.parse_args(argv)

    scraper = RestaurantScraper(name_start=options.name_start)
    setup_logging_from_opts(options, scraper.logger)

    scraper.update()


if __name__ == "__main__":
    main()

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
Scraper for Boston building permits.

http://www.cityofboston.gov/cityclerk/search_reply.asp
"""

from ebdata.retrieval.scrapers.list_detail import SkipRecord
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebpub.db.models import NewsItem
from ebpub.utils.dates import parse_date
from ebpub.utils.text import smart_title
from urllib import urlencode
import datetime
import re

# An opt-out list of businesses to ignore for privacy reasons.
BUSINESS_NAMES_TO_IGNORE = set([
    ('THINK COOL COSMETICS', '176 WASHINGTON ST'),
])

class Scraper(NewsItemListDetailScraper):
    schema_slugs = ['business-licenses']
    has_detail = False
    parse_list_re = re.compile(r'(?s)<div class="mainColTextBlueBold">(?P<name>.*?)</div><br>\s+?<b>Date:</b>(?P<date>.*?)<br>\s+?<b>Type:</b>(?P<business_type>.*?)<br>\s+?<b>Business Address:</b>(?P<location>.*?)<br>\s+?<b>File #:</b>(?P<file_number>.*?)<br>')
    sleep = 1
    uri = 'http://www.cityofboston.gov/cityclerk/search_reply.asp'

    def __init__(self, *args, **kwargs):
        self.start_date = kwargs.pop('start_date', None)
        super(Scraper, self).__init__(*args, **kwargs)

    def find_next_page_url(self, html, current_page_number):
        pattern = r"<a href='(.*?)'>%s</a>" % (current_page_number + 1)
        print pattern
        m = re.search(pattern, html)
        if m is None:
            return None
        return "http://www.cityofboston.gov%s" % m.group(1)

    def list_pages(self):
        if not self.start_date:
            date = datetime.date.today() - datetime.timedelta(days=7)
        else:
            date = self.start_date
        while date <= datetime.date.today():
            page_number = 1
            while 1:
                params = {
                    'whichpage': str(page_number),
                    'pagesize': '10',
                    'name_fold': '',
                    'name_doc': date.strftime('%Y-%m-%d'),
                    'index1': '',
                    'index2': '',
                    'index3': '',
                    'index4': '',
                    'index6': '',
                    'tempday': date.strftime('%d'),
                    'tempmonth': date.strftime('%m'),
                    'tempyear': date.strftime('%Y'),
                }
                html = self.get_html(self.uri + '?' + urlencode(params))
                try:
                    max_pages = int(re.search(r'Page \d+ of (\d+)', html).group(1))
                except AttributeError:
                    break
                yield html
                page_number += 1
                if page_number > max_pages:
                    break
            date = date + datetime.timedelta(days=1)

    def clean_list_record(self, record):
        notes = []
        notes_pats = [r'(?P<value>.*?)\s*\-*\s*(?P<notes>\(?\s*w\/d.*)',
                      r'(?P<value>.*?)\s*\-*\s*(?P<notes>\(?\s*withd.*)', 
                      r'(?P<value>.*?)\s*\-*\s*(?P<notes>\(?\s*ch\s+227\s+sec\s*5A.*)',
                      r'(?P<value>.*?)\s*\-*\s*(?P<notes>\(?\s*ch\s+bus\s+.*)',
                      r'(?P<value>.*?)\s*\-*\s*(?P<notes>\(?\s*c\/l.*)',
                      ]

        # strip notes off of several cruft-prone fields
        for field in ['name', 'business_type', 'location']:
            val = record.get(field, '').strip()
            for pat in notes_pats: 
                m = re.match(pat, val, re.I|re.M)
                if m is not None: 
                    results = m.groupdict()
                    val = results['value']
                    notes.append(results['notes'])
            record[field] = val.strip()

        record['notes'] = notes
        record['location'] = smart_title(record['location'].strip())
        record['date'] = parse_date(record['date'].strip(), '%Y-%m-%d')
        if (record['name'].upper(), record['location'].upper()) in BUSINESS_NAMES_TO_IGNORE:
            raise SkipRecord('Skipping %s (explicitly ignored)' % record['name'])
        if (record['location'] == ''):
            raise SkipRecord('Skipping %s (no location)' % record['name'])
        return record

    def existing_record(self, list_record):
        qs = NewsItem.objects.filter(schema__id=self.schema.id, item_date=list_record['date'])
        qs = qs.by_attribute(self.schema_fields['name'], list_record['name'])
        try:
            return qs[0]
        except IndexError:
            return None

    def save(self, old_record, list_record, detail_record):
        if old_record is not None:
            return
        if list_record['name'].upper() in ['NONE', '']:
            return
        business_type_lookup = self.get_or_create_lookup('business_type', list_record['business_type'], list_record['business_type'], make_text_slug=False)
        attributes = {
            'name': list_record['name'],
            'file_number': list_record['file_number'],
            'business_type': business_type_lookup.id,
            'notes': ','.join(list_record['notes'])[0:255]
        }
        self.create_newsitem(
            attributes,
            title=list_record['name'],
            item_date=list_record['date'],
            location_name=list_record['location']
        )

def main(argv=None):
    import sys
    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    from optparse import OptionParser
    if argv is None:
        argv = sys.argv[1:]
    optparser = OptionParser()
    optparser.add_option('-s', '--start-date',
                         help='Date to start scraping, in YYYY/MM/DD format. If not passed, default is 7 days ago.'
                         )
    add_verbosity_options(optparser)
    opts, args = optparser.parse_args(argv)
    if opts.start_date:
        from ebpub.utils.dates import parse_date
        start_date = parse_date(opts.start_date, '%Y/%m/%d')
    else:
        start_date = None
    scraper = Scraper(start_date=start_date)
    setup_logging_from_opts(opts, scraper.logger)
    scraper.update()

if __name__ == "__main__":
    main()

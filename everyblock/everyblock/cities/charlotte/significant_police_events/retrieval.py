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
Screen scraper for Charlotte police "significant events."
http://maps.cmpdweb.org/significanteventlog/
"""

from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebpub.db.models import NewsItem
from ebpub.utils.dates import parse_date
import re

SOURCE_URL = 'http://maps.cmpdweb.org/cfs/Default.aspx'

class SignificantEventScraper(NewsItemListDetailScraper):
    schema_slugs = ('significant-police-events',)
    has_detail = False
    parse_list_re = re.compile(r'Incident Address</td><td[^>]*>&nbsp;</td><td[^>]*>(?P<address>[^>]*)</td><td[^>]*>Division</td><td[^>]*>(?P<division>[^>]*)</td></tr><tr[^>]*><td[^>]*>(?P<incident_date>[^>]*)</td><td[^>]*>(?P<incident_time>[^>]*)</td><td[^>]*>&nbsp;</td><td[^>]*>(?P<incident_type>[^>]*)</td><td[^>]*>(?P<complaint_number>[^>]*)</td><td[^>]*></td><td[^>]*>(?P<officer>[^>]*)</tr><tr[^>]*><td[^>]*>(?P<description>[^>]*)</td>', re.IGNORECASE | re.DOTALL)

    def list_pages(self):
        yield self.get_html('http://maps.cmpdweb.org/significanteventlog/')

    def clean_list_record(self, record):
        item_datetime = parse_date('%s_%s' % (record['incident_date'].strip(), record['incident_time'].strip()), '%m/%d/%Y_%H:%M', return_datetime=True)
        record['item_date'] = item_datetime.date()
        record['item_time'] = item_datetime.time()
        record['description'] = record['description'].strip()
        return record

    def existing_record(self, record):
        try:
            qs = NewsItem.objects.filter(schema__id=self.schema.id)
            qs = qs.by_attribute(self.schema_fields['complaint_number'], record['complaint_number'])
            return qs[0]
        except IndexError:
            return None

    def save(self, old_record, list_record, detail_record):
        if old_record is not None:
            self.logger.debug('Record already exists')
            return

        division = self.get_or_create_lookup('division', list_record['division'], list_record['division'])
        incident_type = self.get_or_create_lookup('incident_type', list_record['incident_type'], list_record['incident_type'])

        attributes = {
            'division': division.id,
            'incident_type': incident_type.id,
            'complaint_number': list_record['complaint_number'],
            'description': list_record['description'],
            'officer': list_record['officer'],
            'incident_time': list_record['item_time'],
        }
        self.create_newsitem(
            attributes,
            title=incident_type.name,
            item_date=list_record['item_date'],
            location_name=list_record['address'],
        )

if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    SignificantEventScraper().update()

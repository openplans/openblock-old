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
Scraper for Florida lodging inspections.
http://www.myflorida.com/dbpr/sto/file_download/hr_inspection.shtml
"""

from ebdata.retrieval.scrapers.list_detail import SkipRecord
from everyblock.states.florida.restaurants.retrieval import Scraper as RestaurantScraper

# The data is in the same format as restaurant inspections, so we can
# merely subclass the restaurant scraper.

class Scraper(RestaurantScraper):
    schema_slugs = ('lodging-inspections',)

    def __init__(self, city_names, district):
        super(Scraper, self).__init__(city_names, district)
        self.florida_ftp_filename = '%sldinspi.exe' % district

    def clean_list_record(self, record):
        record = super(Scraper, self).clean_list_record(record)

        # Special-case: a bad record identified on 2009-02-11.
        if str(record['inspection_visit_id']) == '3145783' and str(record['license_id']) == '2164597':
            raise SkipRecord('Invalid record')

        return record

class MiamiScraper(Scraper):
    def __init__(self):
        city_names = ['MIAMI', 'AVENTURA', 'BAL HARBOUR', 'BAY HARBOR ISLANDS',
            'BISCAYNE PARK', 'CORAL GABLES', 'CUTLER BAY', 'DORAL', 'EL PORTAL',
            'FLORIDA CITY', 'GOLDEN BEACH', 'HIALEAH', 'HIALEAH GARDENS',
            'HOMESTEAD', 'INDIAN CREEK VILLAGE', 'ISLANDIA', 'KEY BISCAYNE',
            'MEDLEY', 'MIAMI BEACH', 'MIAMI GARDENS', 'MIAMI LAKES',
            'MIAMI SHORES', 'MIAMI SPRINGS', 'NORTH BAY VILLAGE', 'NORTH MIAMI',
            'NORTH MIAMI BEACH', 'OPA-LOCKA', 'PALMETTO BAY', 'PINECREST',
            'SOUTH MIAMI', 'SUNNY ISLES BEACH', 'SURFSIDE', 'SWEETWATER',
            'VIRGINIA GARDENS', 'WEST MIAMI']
        super(MiamiScraper, self).__init__(city_names, 1)

if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    MiamiScraper().update()

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
Boston city press release scraper.

http://www.cityofboston.gov/news/
Example: http://www.cityofboston.gov/news/default.aspx?id=3910
"""

from ebdata.blobs.scrapers import IncrementalCrawler
import re

class BostonCityPressReleaseCrawler(IncrementalCrawler):
    schema = 'city-press-releases'
    seed_url = 'http://www.cityofboston.gov/news/'
    date_headline_re = re.compile(r'(?si)<span id="lblTitle">(?P<article_headline>[^>]*)</span>.*?<span id="lblDate">(?P<article_date>\d\d?/\d\d?/\d\d\d\d)</span>')
    date_format = '%m/%d/%Y'
    max_blanks = 8

    def public_url(self, id_value):
        return 'http://www.cityofboston.gov/news/default.aspx?id=%s' % id_value

    def id_for_url(self, url):
        return url.split('id=')[1]

if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    BostonCityPressReleaseCrawler().update()

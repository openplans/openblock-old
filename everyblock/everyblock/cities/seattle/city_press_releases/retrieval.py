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
Seattle city press release scraper.

http://www.seattle.gov/news/
Example: http://www.seattle.gov/news/detail.asp?ID=8622
"""

from ebdata.blobs.scrapers import IncrementalCrawler
import re

class SeattleCityPressReleaseCrawler(IncrementalCrawler):
    schema = 'city-press-releases'
    seed_url = 'http://www.seattle.gov/news/'
    date_headline_re = re.compile(r'(?si)<b>SUBJECT:</b>&nbsp;&nbsp; (?P<article_headline>.*?)\s*</tr>.*?<b>FOR IMMEDIATE RELEASE:&nbsp;&nbsp;&nbsp;</b><br>\s*(?P<article_date>\d\d?/\d\d?/\d\d\d\d)')
    date_format = '%m/%d/%Y'
    max_blanks = 8

    def public_url(self, id_value):
        return 'http://www.seattle.gov/news/detail.asp?ID=%s' % id_value

    def id_for_url(self, url):
        return url.split('ID=')[1]

if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    SeattleCityPressReleaseCrawler().update()

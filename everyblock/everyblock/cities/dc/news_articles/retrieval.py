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
Site-specific scrapers for DC news sources that don't have RSS feeds.
"""

from ebdata.blobs.scrapers import IncrementalCrawler
import re

class WashingtonCityPaperCrawler(IncrementalCrawler):
    schema = 'news-articles'
    seed_url = 'http://www.washingtoncitypaper.com/'
    date_headline_re = re.compile(r'(?s)<h1 class="article-headline">(?P<article_headline>.*?)</h1>.*?<span class="article-date">Posted: (?P<article_date>\w+ \d\d?, \d\d\d\d)</span>')
    date_format = '%B %d, %Y'
    max_blanks = 7

    def public_url(self, id_value):
        return 'http://www.washingtoncitypaper.com/display.php?id=%s' % id_value

    def retrieval_url(self, id_value):
        return 'http://www.washingtoncitypaper.com/printerpage.php?id=%s' % id_value

    def id_for_url(self, url):
        return url.split('id=')[1]

if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    WashingtonCityPaperCrawler().update()

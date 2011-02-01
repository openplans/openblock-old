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
Site-specific scrapers for NYC news sources that don't have RSS feeds.
"""

from ebdata.blobs.scrapers import IncrementalCrawler
import re

class BrooklynEagleCrawler(IncrementalCrawler):
    schema = 'news-articles'
    seed_url = 'http://www.brooklyneagle.com/'
    date_headline_re = re.compile(r'<b><span class="f24">(?P<article_headline>.*?)</span></b><div align="justify" class="f11">.*?, published online <span[^>]*>(?P<article_date>\d\d?-\d\d?-\d\d\d\d)</span></div>')
    date_format = '%m-%d-%Y'
    max_blanks = 7

    def public_url(self, id_value):
        # Note that the category_id doesn't matter.
        return 'http://www.brooklyneagle.com/categories/category.php?id=%s' % id_value

    def id_for_url(self, url):
        return url.split('id=')[1]

class Ny1Crawler(IncrementalCrawler):
    schema = 'news-articles'
    seed_url = 'http://www.ny1.com/'
    date_headline_re = re.compile(r'<span id="ArPrint_lblArHeadline" class="blackheadline1">(?P<article_headline>.*?)</span><br />\s*<span id="ArPrint_lblArPostDate" class="black11">(?:<strong>Updated&nbsp;</strong>)?(?P<article_date>\d\d?/\d\d?/\d\d\d\d)')
    date_format = '%m/%d/%Y'
    max_blanks = 7

    def public_url(self, id_value):
        return 'http://www.ny1.com/Default.aspx?ArID=%s' % id_value

    def retrieval_url(self, id_value):
        return 'http://www.ny1.com/printarticle.aspx?ArID=%s' % id_value

    def id_for_url(self, url):
        return url.split('ArID=')[1]

if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    BrooklynEagleCrawler().update()
    Ny1Crawler().update()

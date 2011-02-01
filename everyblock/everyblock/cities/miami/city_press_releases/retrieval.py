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

from ebdata.blobs.scrapers import PageAreaCrawler
import re
import urlparse

class MiamiPressReleaseScraper(PageAreaCrawler):
    schema = 'city-press-releases'
    seed_url = 'http://www.miamigov.com/cms/comm/1724.asp'
    date_headline_re = re.compile(r'(?si)For Immediate Release<br>(?:[a-z]+, )?(?P<article_date>[a-z]+ \d\d?, \d\d\d\d)</p>.*?<FONT size=5>(?P<article_headline>.*?)</FONT>')
    date_format = '%B %d, %Y'

    def get_links(self, html):
        m = re.search(r'(?si)<div id="pageHeader">\s*News&nbsp;\s*</div>(.*?)<hr id="footerHR" />', html)
        area = m.group(1)
        return [urlparse.urljoin(self.seed_url, link) for link in re.findall('<a href="([^"]*)"', area)]

class CoralGablesPressReleaseScraper(PageAreaCrawler):
    schema = 'city-press-releases'
    seed_url = 'http://www.citybeautiful.net/CGWeb/newslist.aspx?newsid=ALL'
    date_headline_re = re.compile(r"(?si)<font class ='bodycopy'>(?P<article_date>\d\d?/\d\d?/\d\d\d\d): </font><font class='headline'>(?P<article_headline>.*?)</font>")
    date_format = '%m/%d/%Y'

    def get_links(self, html):
        return [urlparse.urljoin(self.seed_url, link) for link in re.findall("<a href='([^']*)'>Read full story</a>", html)]

if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    MiamiPressReleaseScraper().update()
    CoralGablesPressReleaseScraper().update()

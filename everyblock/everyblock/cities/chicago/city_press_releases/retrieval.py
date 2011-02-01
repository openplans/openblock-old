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

from ebdata.blobs.scrapers import IncrementalCrawler
import re

class ChicagoCityPressReleaseCrawler(IncrementalCrawler):
    schema = 'city-press-releases'
    seed_url = 'http://egov.cityofchicago.org/'
    date_headline_re = re.compile(r'(?s)E-mail: <a href="mailto:[^"]*">.*?</a><br>\s*(?P<article_date>.*?)\s*</td>\s*</tr>\s*<tr>\s*<td align="center" class="bodytextbold">(?P<article_headline>.*?)</td>')
    date_format = '%A, %B %d, %Y'
    max_blanks = 60

    def public_url(self, id_value):
        return 'http://egov.cityofchicago.org/city/webportal/portalContentItemAction.do?contenTypeName=COC_EDITORIAL&topChannelName=HomePage&contentOID=%s' % id_value

    def retrieval_url(self, id_value):
        return 'http://egov.cityofchicago.org/city/webportal/jsp/content/showNewsItem.jsp?print=true&contenTypeName=1006&contentOID=%s' % id_value

    def id_for_url(self, url):
        return url.split('contentOID=')[1]

if __name__ == "__main__":
    from ebdata.retrieval import log_debug
    ChicagoCityPressReleaseCrawler().update()

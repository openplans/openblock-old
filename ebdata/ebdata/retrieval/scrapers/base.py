#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

from ebdata.retrieval import Retriever
import datetime
import logging

class ScraperBroken(Exception):
    "Something changed in the underlying data format and broke the scraper."
    pass

class BaseScraper(object):
    """
    Base class for all scrapers in ebdata.retrieval.scrapers.
    """
    logname = 'basescraper'
    sleep = 0

    def __init__(self, use_cache=True):
        if not use_cache:
            self.retriever = Retriever(cache=None, sleep=self.sleep)
        else:
            self.retriever = Retriever(sleep=self.sleep)
        self.logger = logging.getLogger('eb.retrieval.%s' % self.logname)
        self.start_time = datetime.datetime.now()

    def update(self):
        'Run the scraper.'
        raise NotImplementedError()

    def fetch_data(self, *args, **kwargs):
        return self.retriever.fetch_data(*args, **kwargs)

    def get_html(self, *args, **kwargs):
        """An alias for fetch_data().
        For backward compatibility.
        """
        return self.fetch_data(*args, **kwargs)

    @classmethod
    def parse_html(cls, html):
        from lxml import etree
        from cStringIO import StringIO
        return etree.parse(StringIO(html), etree.HTMLParser())

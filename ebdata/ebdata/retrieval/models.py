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

from django.db import models
from ebpub.db.models import NewsItem, Schema

LIST_PAGE = 1
DETAIL_PAGE = 2
PAGE_TYPE_CHOICES = (
    (LIST_PAGE, 'list'),
    (DETAIL_PAGE, 'detail')
)

class ScrapedPage(models.Model):
    page_type = models.SmallIntegerField(choices=PAGE_TYPE_CHOICES)
    schema = models.ForeignKey(Schema)
    when_crawled = models.DateTimeField()
    url = models.URLField()
    html = models.TextField()

    def __unicode__(self):
        return u'HTML from %s - %s' % (self.url, self.when_crawled)

class NewsItemHistoryManager(models.Manager):
    def save_page_if_needed(self, page):
        """Call save() on a Page object if it hasn't already been saved."""
        if page is not None and page.pk is None:
            page.save()

    def record_history(self, news_item, page):
        """Associates a page with a NewsItem."""
        self.save_page_if_needed(page)
        self.create(news_item=news_item, page=page)

class NewsItemHistory(models.Model):
    """Essentially a ManyToMany relation between ScrapedPage and NewsItem"""
    news_item = models.ForeignKey(NewsItem)
    page = models.ForeignKey(ScrapedPage)
    objects = NewsItemHistoryManager()

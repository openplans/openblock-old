#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebblog
#
#   ebblog is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebblog is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebblog.  If not, see <http://www.gnu.org/licenses/>.
#

from django.db import models

class Entry(models.Model):
    pub_date = models.DateTimeField()
    author = models.CharField(max_length=32, help_text='Use the full name, e.g., "John Lennon".')
    slug = models.CharField(max_length=32)
    headline = models.CharField(max_length=255)
    summary = models.TextField(help_text='Use plain text (no HTML).')
    body = models.TextField(help_text='Use raw HTML, including &lt;p&gt; tags.')

    class Meta:
        verbose_name_plural = 'entries'

    def __unicode__(self):
        return self.headline

    def url(self):
        return "/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(), self.slug)

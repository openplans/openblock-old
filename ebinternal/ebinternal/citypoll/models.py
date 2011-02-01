#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebinternal
#
#   ebinternal is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebinternal is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebinternal.  If not, see <http://www.gnu.org/licenses/>.
#

from django.db import models

class City(models.Model):
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=2, blank=True)

    def __unicode__(self):
        return self.pretty_name

    def pretty_name(self):
        if self.state:
            return u'%s, %s' % (self.city, self.state)
        return self.city

    def url(self):
        return '/citypoll/%s/' % self.id

class Vote(models.Model):
    # The "normalized" version of the requested city.
    city = models.ForeignKey(City, blank=True, null=True)

    # The raw data that's submitted to us.
    city_text = models.CharField(max_length=64)
    email = models.CharField(max_length=128)
    notes = models.TextField()

    # Metadata about the submission.
    ip_address = models.CharField(max_length=225, blank=True) # Might be comma-separated list.
    date_received = models.DateTimeField()

    def __unicode__(self):
        return u'%s at %s' % (self.city_text, self.date_received)

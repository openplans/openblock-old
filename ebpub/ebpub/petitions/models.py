#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

from django.db import models
from ebpub.db.models import Schema

class Petition(models.Model):
    # NULL schema means a city-level petition (i.e., not tied to a schema).
    schema = models.ForeignKey(Schema, blank=True, null=True)
    slug = models.CharField(max_length=64, unique=True, blank=True)
    data_name = models.CharField(max_length=64, blank=True)
    teaser = models.CharField(max_length=255, blank=True)
    petition = models.TextField()
    creation_date = models.DateField()

    def __unicode__(self):
        return self.full_data_name()

    def full_data_name(self):
        if self.schema:
            return self.schema.name
        return self.data_name

class Petitioner(models.Model):
    petition = models.ForeignKey(Petition)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)
    email = models.EmailField()
    notes = models.TextField()
    date_signed = models.DateTimeField()
    ip_address = models.IPAddressField()

    def __unicode__(self):
        return self.name

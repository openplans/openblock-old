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

from django.contrib.gis.db import models
from ebpub.streets.models import Block
from ebpub.streets.models import Intersection

class GeocoderCache(models.Model):
    normalized_location = models.CharField(max_length=255, db_index=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    location = models.PointField()
    block = models.ForeignKey(Block, blank=True, null=True)
    intersection = models.ForeignKey(Intersection, blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.normalized_location

    @classmethod
    def populate(cls, normalized_location, address):
        """
        Populates the cache from an Address object.
        """
        if address['point'] is None:
            return
        obj = cls()
        obj.normalized_location = normalized_location
        for field in ('address', 'city', 'state', 'zip'):
            setattr(obj, field, address[field])
        for relation in ['block', 'intersection_id']:
            if relation in address:
                setattr(obj, relation, address[relation])
        obj.location = address['point']
        obj.save()

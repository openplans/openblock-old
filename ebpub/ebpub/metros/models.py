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

from django.conf import settings
from django.contrib.gis.db import models

class MetroManager(models.GeoManager):
    def get_current(self):
        return self.get(short_name=settings.SHORT_NAME)

    def containing_point(self, point):
        # First pass, just check to see if it's in the bounding box --
        # this is faster for checking across all metros
        metros = self.filter(location__bbcontains=point)
        n = metros.count()
        if not n:
            raise Metro.DoesNotExist()
        else:
            # Now do the slower but more accurate lookup to see if the
            # point is completely within the actual bounds of the
            # metro. Note that we could also have hit two or more
            # metros if they have overlapping bounding boxes.
            matches = 0
            for metro in metros:
                if metro.location.contains(point):
                    matches += 1
            if matches > 1:
                # Something went wrong, it would mean the metros have
                # overlapping borders
                raise Exception('more than one metro found to contain this point')
            elif matches == 0:
                raise Metro.DoesNotExist()
            else:
                return metro

class Metro(models.Model):
    """
    Note this is currently not used in the openblock codebase;
    settings.METRO_LIST is used instead.

    Metro is an in-database representation of a metropolitan region
    covered by one OpenBlock site.  These look to be equivalent to the
    data in settings.METRO_LIST.

    It's unclear what the history is. Possibly, everyblock.com was in
    the process of transitioning to in-database metro data at the time
    they released their source code?

    Given that the concept of 'metros' is a lot less important to
    OpenBlock than it was to Everyblock.com, we can possibly safely
    remove this.
    """
    name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=64, unique=True)
    metro_name = models.CharField(max_length=64)
    population = models.IntegerField(null=True, blank=True)
    area = models.IntegerField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    multiple_cities = models.BooleanField(default=False)
    state = models.CharField(max_length=2)
    state_name = models.CharField(max_length=64)
    location = models.MultiPolygonField()
    objects = MetroManager()

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'state')

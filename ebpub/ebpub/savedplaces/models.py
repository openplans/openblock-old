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
from ebpub.db.models import Location
from ebpub.streets.models import Block
from ebpub.constants import BLOCK_FUZZY_DISTANCE_METERS

class SavedPlace(models.Model):
    """
    Either a db.Location or streets.Block that a user saves a reference to
    so they can easily find it later.
    """

    objects = models.GeoManager()

    user_id = models.IntegerField()

    block_center = models.PointField(null=True, blank=True,
                                     help_text=u'Point representing the center of a related block.')
    location = models.ForeignKey(Location, blank=True, null=True)
    nickname = models.CharField(max_length=128, blank=True)

    def __unicode__(self):
        return u'User %s: %s' % (self.user_id, self.place.pretty_name)

    @property
    def place(self):
        return self._get_block() or self.location

    @property
    def user(self):
        if not hasattr(self, '_user_cache'):
            from ebpub.accounts.models import User
            try:
                self._user_cache = User.objects.get(id=self.user_id)
            except User.DoesNotExist:
                self._user_cache = None
        return self._user_cache

    def pid(self):
        """Place ID as used by ebpub.db.views
        """
        from ebpub.utils.view_utils import make_pid
        if self.block_center:
            block = self._get_block()
            return make_pid(block, 8)
        else:
            return make_pid(self.location)

    def clean(self):
        from django.core.exceptions import ValidationError
        error = ValidationError("SavedPlace must have either a Location or a block_center, but not both")
        if self.block_center and self.location_id:
            raise error
        if not (self.block_center or self.location_id):
            raise error

    def _get_block(self):
        if self.block_center is None:
            return None
        # We buffer the center a bit because exact intersection
        # doesn't always get a match.
        from ebpub.utils.mapmath import buffer_by_meters
        geom = buffer_by_meters(self.block_center, BLOCK_FUZZY_DISTANCE_METERS)
        blocks = Block.objects.filter(geom__intersects=geom)
        if not blocks:
            raise Block.DoesNotExist("No block found at lat %s, lon %s" % (self.block_center.y, self.block_center.x))
        # If there's more than one this close, we don't really care.
        return blocks[0]

    block = property(_get_block)

    def name(self):
        if self.location:
            return self.location.pretty_name
        else:
            block = self._get_block()
            if block:
                return u'%s block%s around %s' % (self.radius, (self.radius != 1 and 's' or ''), block.pretty_name)
        return u'(no name)'

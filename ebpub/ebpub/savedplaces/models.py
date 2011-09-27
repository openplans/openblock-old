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
from ebpub.db.models import Location
from ebpub.streets.models import Block

class SavedPlace(models.Model):
    """
    Either a db.Location or streets.Block that a user saves a reference to
    so they can easily find it later.
    """
    user_id = models.IntegerField()
    block = models.ForeignKey(Block, blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True)
    nickname = models.CharField(max_length=128, blank=True)

    def __unicode__(self):
        return u'User %s: %u' % (self.user_id, self.place.pretty_name)

    @property
    def place(self):
        return self.block_id and self.block or self.location

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
        if self.block_id:
            return make_pid(self.block, 8)
        else:
            return make_pid(self.location)

    def clean(self):
        from django.core.exceptions import ValidationError
        error = ValidationError("SavedPlace must have either a Location or a Block, but not both")
        if self.block_id and self.location_id:
            raise error
        if not (self.block_id or self.location_id):
            raise error

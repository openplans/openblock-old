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
from django.db.models.signals import post_save
from ebpub.db.models import Schema
import ebpub.accounts.models
from ebpub.openblockapi.apikey.models import MAX_KEYS

class HiddenSchema(models.Model):
    user_id = models.IntegerField()
    schema = models.ForeignKey(Schema)

    @property
    def user(self):
        if not hasattr(self, '_user_cache'):
            from ebpub.accounts.models import User
            try:
                self._user_cache = User.objects.get(id=self.user_id)
            except User.DoesNotExist:
                self._user_cache = None
        return self._user_cache

    def __unicode__(self):
        return u'<HiddenSchema %s for user %s>' % (self.user_id, self.schema.slug)


class Profile(models.Model):
    """
    Currently just metadata about the user's API keys, but this would
    be the logical place to hang preferences information and such;
    hence putting this in the preferences app.
    """
    user = models.ForeignKey(ebpub.accounts.models.User, unique=True)

    max_keys = models.IntegerField(default=MAX_KEYS,
                                   help_text="How many API keys can this user have?")

    def available_keys(self):
        """
        How many *more* API keys can this user get?
        """
        allowed = self.max_keys
        return max(0, allowed - self.user.keys.count())

    def can_make_api_key(self):
        if self.available_keys() > 0:
            return True

    def __unicode__(self):
        return "Profile: user %d" % (self.user_id)

# Need to explicitly create profiles on user save, as per django docs:
# https://docs.djangoproject.com/en/1.3/topics/auth/#storing-additional-information-about-users
def post_save_user(sender, **kwargs):
    profile, created = Profile.objects.get_or_create(user=kwargs['instance'])

post_save.connect(post_save_user, sender=ebpub.accounts.models.User)

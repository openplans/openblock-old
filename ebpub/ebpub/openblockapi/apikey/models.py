#   Copyright 2011 OpenPlans and contributors
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

"""
REST API Key model implementation derived from django-apikey,
copyright (c) 2011 Steve Scoursen and Jorge Eduardo Cardona.
BSD license.
http://pypi.python.org/pypi/django-apikey
"""

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime


# Changing this would require a migration
KEY_SIZE = 32

try:
    MAX_KEYS = settings.MAX_KEYS_PER_USER
except AttributeError:
    MAX_KEYS = -1


class ApiKey(models.Model):
    user = models.ForeignKey(User, related_name='keys')
    key = models.CharField(max_length=KEY_SIZE, unique=True)
    logged_ip = models.IPAddressField(null=True)
    last_used = models.DateTimeField(default=datetime.utcnow)

    class Meta:
        db_table = 'key_apikey'

    def login(self, ip_address):
        self.logged_ip = ip_address
        self.save()

    def logout(self):
        self.logged_ip = None
        self.save()

    def __unicode__(self):
        return self.key

def generate_unique_api_key():
    """random string suitable for use with ApiKey
    """
    # From http://jetfar.com/simple-api-key-generation-in-python/
    import base64
    import hashlib
    import random
    api_key = ''
    while len(api_key) < KEY_SIZE:
        more_key = str(random.getrandbits(256))
        more_key = hashlib.sha256(more_key).hexdigest()
        more_key = base64.b64encode(
            more_key,
            random.choice(['rA','aZ','gQ','hH','hG','aR','DD']))
        more_key = more_key.rstrip('=')
        api_key += more_key
    api_key = api_key[:KEY_SIZE]
    return api_key

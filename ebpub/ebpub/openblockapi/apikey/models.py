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
    MAX_KEYS = settings.API_MAX_KEYS
except AttributeError:
    MAX_KEYS = -1

class ApiKeyProfile(models.Model):
    user = models.OneToOneField(User, related_name='key_profile',
                                )
    max_keys = models.IntegerField(default=MAX_KEYS)

    class Meta:
        db_table = 'key_apikeyprofile'

    def available_keys(self):
        if self.max_keys == -1:
            return 'Unlimited'
        return self.max_keys - self.keys.count()

    def can_make_api_key(self):
        if self.available_keys() > 0:
            return True

    def __unicode__(self):
        return "ApiKeyProfile: %s, %s" % (self.keys.count(),
                                          self.max_keys)

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

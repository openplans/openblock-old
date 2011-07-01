from django.contrib.admin.sites import NotRegistered
from django.contrib.gis import admin
from django.contrib.admin import ModelAdmin
from django.forms import ModelForm
from django.forms import CharField
from django.forms import IPAddressField
from key.models import KEY_SIZE
from key.models import ApiKey

try:
    admin.site.unregister(ApiKey)
except NotRegistered:
    pass # don't care

class ApiKeyForm(ModelForm):
    """
    Generate a random API key if one isn't provided.
    """

    class Meta:
        model = ApiKey

    key = CharField(max_length=KEY_SIZE, required=False,
                    help_text=u'If not provided, a random key will be generated.')

    logged_ip = IPAddressField(required=False)

    def clean(self):
        apikey = self.cleaned_data.get('key') or ''
        if not apikey:
            # 'key' is required, but we want to allow generating it server-side.
            # so we remove its errors if it's not provided.
            # Note that we can't just define self.clean_key() because that's never
            # called if the key isn't provided.
            self._errors.pop('key', None)
            while len(apikey) <= KEY_SIZE:
                # From http://jetfar.com/simple-api-key-generation-in-python/
                import base64
                import hashlib
                import random
                apikey = str(random.getrandbits(256))
                apikey = hashlib.sha256(apikey).hexdigest()
                apikey = base64.b64encode(
                    apikey,
                    random.choice(['rA','aZ','gQ','hH','hG','aR','DD']))
                apikey = apikey.rstrip('=')
            apikey = apikey[:KEY_SIZE]
            self.cleaned_data['key'] = apikey
            if hasattr(self, 'clean_key'):
                # NOW we can call this...
                self.cleaned_data['key'] = self.clean_key()

        # For logged IP, convert blank to NULL
        self.cleaned_data['logged_ip'] = self.cleaned_data.get('logged_ip') or None
        return self.cleaned_data


class ApiKeyAdminEnhanced(ModelAdmin):
    form = ApiKeyForm

    list_display = ('key', 'user', 'logged_ip', 'last_used')

admin.site.register(ApiKey, ApiKeyAdminEnhanced)

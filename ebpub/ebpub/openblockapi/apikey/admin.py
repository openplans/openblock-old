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


from django.contrib.admin import ModelAdmin
from django.contrib.gis import admin
from django.forms import CharField
from django.forms import IPAddressField
from django.forms import ModelForm
from django.forms import ValidationError
from .models import KEY_SIZE
from .models import ApiKey
from .models import generate_unique_api_key

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
        profile = self.cleaned_data.get('user').user.get_profile()
        if self.instance.pk is None:
            # We're creating a new instance
            if not profile.can_make_api_key():
                raise ValidationError("User already has max number of keys")

        apikey = self.cleaned_data.get('key') or ''

        if not apikey:
            # 'key' is required, but we want to allow generating it server-side.
            # so we remove its errors if it's not provided.
            # Note that we can't just define self.clean_key() because that's never
            # called if the key isn't provided.
            self._errors.pop('key', None)
            apikey = generate_unique_api_key()
            self.cleaned_data['key'] = apikey
            if hasattr(self, 'clean_key'):
                # NOW we can call this...
                self.cleaned_data['key'] = self.clean_key()

        # For logged IP, convert blank to NULL
        self.cleaned_data['logged_ip'] = self.cleaned_data.get('logged_ip') or None
        return self.cleaned_data


class ApiKeyAdmin(ModelAdmin):
    form = ApiKeyForm

    list_display = ('key', 'user', 'logged_ip', 'last_used')

admin.site.register(ApiKey, ApiKeyAdmin)


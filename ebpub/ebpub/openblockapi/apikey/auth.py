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

from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from .models import ApiKey

KEY_HEADER = 'HTTP_X_OPENBLOCK_KEY'

class APIKeyBackend(object):
    """
    Django authentication backend purely by API key.
    """

    # Not sure yet if we really want to use this as an auth backend;
    # we certainly don't want it in the global settings.AUTHENTICATION_BACKENDS
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, key=None, ip_address=None):
        if not key:
            return None

        user, key_instance = self._get_user_and_key(key)
        if None in (user, key_instance):
            return None
        key_instance.login(ip_address)
        return user

    def get_user(self, user_id):
        """user_id is an API key.
        """
        return self._get_user_and_key(user_id)[1]


    def _get_user_and_key(self, key):
        try:
            key_instance = ApiKey.objects.get(key=key)
        except ApiKey.DoesNotExist:
            return (None, None)
        return key_instance.user, key_instance

def check_api_authorization(request):
    """
    Check API access based on the current request.

    Currently requires that either the user is logged in (eg. via
    basic auth), or there is a valid API key in the 'apikey' request
    parameter.  If either fails, raises ``PermissionDenied``.

    This should become more configurable.
    """
    if request.user.is_authenticated():
        user = request.user
        if user.is_active:
            return True
        else:
            raise PermissionDenied("Your account is disabled.")
    else:
        ip_address = request.META['REMOTE_ADDR']
        key = request.META.get(KEY_HEADER)
        user = APIKeyBackend().authenticate(key=key, ip_address=ip_address)
        if user is None:
            raise PermissionDenied("invalid key?")
        if user.is_active:
            # login() expects a dotted name at user.backend.
            user.backend = 'ebpub.openblockapi.authentication.APIKeyBackend'
            login(request, user)
            return True
        else:
            raise PermissionDenied("Your account is disabled.")


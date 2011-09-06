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

from django.contrib.auth.models import User
import constants # relative import

UNDEFINED = 123

class LazyUser(User):
    # This class is a transparent wrapper around User that hits the database
    # only after an attribute is accessed.
    def __init__(self, user_id):
        self.user_id = user_id
        self._user_cache = UNDEFINED

    def __getattr__(self, name):
        # Optimization: There's no need to hit the database if we're just
        # getting the ID.
        if name == 'id':
            return self.user_id

        if self._user_cache == UNDEFINED:
            from ebpub.accounts.models import User
            try:
                self._user_cache = User.objects.get(id=self.user_id)
            except User.DoesNotExist:
                self._user_cache = None
        return getattr(self._user_cache, name)

class LazyUserDescriptor(object):
    # This class uses a Python descriptor so that a LazyUser isn't
    # actually created until request.user is accessed.
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user'):
            try:
                user_id = request.session[constants.USER_SESSION_KEY]
            except KeyError:
                from ebpub.accounts.models import AnonymousUser
                user = AnonymousUser()
            else:
                user = LazyUser(user_id)
            request._cached_user = user
        return request._cached_user

class UserMiddleware(object):
    def process_request(self, request):
        request.__class__.user = LazyUserDescriptor()
        return None

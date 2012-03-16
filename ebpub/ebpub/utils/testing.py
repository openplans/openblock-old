#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.utils.importlib import import_module
import django.test.client


class RequestFactory(django.test.client.RequestFactory):
    """Thin wrapper around django.test.client.RequestFactory that
    adds a .session attribute to the request.
    (Asked for this to be added upstream, but was closed WONTFIX
    https://code.djangoproject.com/ticket/15736)
    """

    def request(self, **request):
        """
        Construct a generic request object, with a .session attribute
        as if SessionMiddleware were active.
        """
        req = super(RequestFactory, self).request(**request)
        req.session = self._session()
        return req


    def _session(self):
        """
        Obtains the current session variables.
        """
        if 'django.contrib.sessions' in settings.INSTALLED_APPS:
            engine = import_module(settings.SESSION_ENGINE)
            cookie = self.cookies.get(settings.SESSION_COOKIE_NAME, None)
            if cookie:
                return engine.SessionStore(cookie.value)
        return {}

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

from django.conf import settings
from constants import EMAIL_SESSION_KEY # relative import

def user(request):
    # Makes 'USER' and 'USER_EMAIL' available in templates.
    if not request.user.is_anonymous():
        return {'DEBUG': settings.DEBUG, 'USER': request.user, 'USER_EMAIL': request.session[EMAIL_SESSION_KEY]}
    else:
        return {'DEBUG': settings.DEBUG, 'USER': None, 'USER_EMAIL': None}

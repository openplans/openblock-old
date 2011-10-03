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

"""
Custom template tags for dealing with json.
"""

from django import template
from django.conf import settings
from django.utils import simplejson

register = template.Library()


def json_value(value, arg=None):
    data = simplejson.loads(value)
    if arg is not None:
        try:
            return data[arg]
        except (KeyError, IndexError):
            if settings.DEBUG:
                raise
            return None
    return data

register.filter('json_value', json_value)

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
URL patterns for REST API Key views.
Derived from django-apikey,
copyright (c) 2011 Steve Scoursen and Jorge Eduardo Cardona.
BSD license.
http://pypi.python.org/pypi/django-apikey
"""

from django.conf.urls.defaults import *


urlpatterns = patterns('ebpub.openblockapi.apikey.views',
                       url(r'^create_key/$', 'generate_key', 
                           name='api_create_key' ),
                       url(r'^keys/$', 'list_keys',
                           name='api_list_keys' ),
                       url(r'^delete_key/$', 'delete_key',
                           name='api_delete_key' ),
                       )

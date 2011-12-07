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
Signals sent when saving REST API Keys.
Derived from django-apikey,
copyright (c) 2011 Steve Scoursen and Jorge Eduardo Cardona.
BSD license.
http://pypi.python.org/pypi/django-apikey
"""

from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from .models import ApiKey

def save_api_key( sender, instance, created, **kwargs ):
    try:
        instance.user.get_profile().save()
    except:
        pass
post_save.connect(save_api_key, sender=ApiKey)


def post_delete_api_key( sender, instance, **kwargs ):
    try:
        instance.user.get_profile().save()
    except:
        pass
post_delete.connect(post_delete_api_key, sender=ApiKey)

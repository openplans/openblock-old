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

from django import http
from ebpub.db.models import Schema
from ebpub.preferences.models import HiddenSchema

def ajax_save_hidden_schema(request):
    """
    Creates a HiddenSchema for request.POST['schema'] and request.user.
    """
    if request.method != 'POST':
        raise http.Http404()
    if 'schema' not in request.POST:
        raise http.Http404('Missing schema')
    if request.user.is_anonymous():
        raise http.Http404('Not logged in')

    # Validate that the HiddenSchema hasn't already been created for this user,
    # to avoid duplicates.
    try:
        schema = Schema.public_objects.get(slug=request.POST['schema'])
        sp = HiddenSchema.objects.get(user_id=request.user.id, schema=schema)
    except Schema.DoesNotExist:
        return http.HttpResponse('0') # Schema doesn't exist.
    except HiddenSchema.DoesNotExist:
        pass
    else:
        return http.HttpResponse('0') # Already exists.

    HiddenSchema.objects.create(user_id=request.user.id, schema=schema)
    return http.HttpResponse('1')

def ajax_remove_hidden_schema(request):
    """
    Removes the HiddenSchema for request.POST['schema'] and request.user.
    """
    if request.method != 'POST':
        raise http.Http404()
    if 'schema' not in request.POST:
        raise http.Http404('Missing schema')
    if request.user.is_anonymous():
        raise http.Http404('Not logged in')

    try:
        hidden_schema = HiddenSchema.objects.filter(user_id=request.user.id, schema__slug=request.POST['schema'])
    except HiddenSchema.DoesNotExist:
        # The schema didn't exist. This is a no-op.
        return http.HttpResponse('0')
    hidden_schema.delete()
    return http.HttpResponse('1')

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
from django.utils import simplejson
from ebpub.savedplaces.models import SavedPlace
from ebpub.streets.models import Block
from ebpub.utils.view_utils import parse_pid

def ajax_save_place(request):
    """
    Creates a SavedPlace for request.POST['pid'] and request.user.
    """
    if request.method != 'POST':
        raise http.Http404()
    if 'pid' not in request.POST:
        raise http.Http404('Missing pid')
    if request.user.is_anonymous():
        raise http.Http404('Not logged in')
    place, block_radius, xy_radius = parse_pid(request.POST['pid'])
    kwargs = {'user_id': request.user.id}
    if isinstance(place, Block):
        block, location = place, None
        kwargs['block__id'] = place.id
    else:
        block, location = None, place
        kwargs['location__id'] = place.id

    # Validate that the SavedPlace hasn't already been created for this user,
    # to avoid duplicates.
    try:
        SavedPlace.objects.get(**kwargs)
    except SavedPlace.DoesNotExist:
        pass
    else:
        return http.HttpResponse('0') # Already exists.

    savedplace = SavedPlace(
        user_id=request.user.id,
        block=block,
        location=location,
        nickname=request.POST.get('nickname', '').strip(),
    )
    savedplace.full_clean()
    savedplace.save()
    return http.HttpResponse('1')

def ajax_remove_place(request):
    """
    Removes the SavedPlace for request.POST['pid'] and request.user.
    """
    if request.method != 'POST':
        raise http.Http404()
    if 'pid' not in request.POST:
        raise http.Http404('Missing pid')
    if request.user.is_anonymous():
        raise http.Http404('Not logged in')

    place, block_radius, xy_radius = parse_pid(request.POST['pid'])
    kwargs = {'user_id': request.user.id}
    if isinstance(place, Block):
        block, location = place, None
        kwargs['block__id'] = place.id
    else:
        block, location = None, place
        kwargs['location__id'] = place.id

    SavedPlace.objects.filter(**kwargs).delete()
    return http.HttpResponse('1')

def json_saved_places(request):
    """
    Returns JSON of SavedPlaces for request.user, or an empty list
    if the user isn't logged in.
    """
    if request.user.is_anonymous():
        result = []
    else:
        result = [{'name': sp.place.pretty_name, 'url': sp.place.url()} for sp in SavedPlace.objects.filter(user_id=request.user.id)]
    return http.HttpResponse(simplejson.dumps(result), mimetype='application/javascript')

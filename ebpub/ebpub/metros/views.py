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

from django.contrib.gis.geos import Point
from django.http import HttpResponse, Http404
from django.utils import simplejson as json
from ebpub.metros.models import Metro

def lookup_metro(request):
    """
    Lookups up a metro that contains the point represented by the two
    GET parameters, `lng' and `lat'.

    Returns a JSON object representing the Metro, minus the actual
    geometry.
    """
    try:
        lng = float(request.GET['lng'])
        lat = float(request.GET['lat'])
    except (KeyError, ValueError, TypeError):
        raise Http404('Missing/invalid lng and lat query parameters')

    try:
        metro = Metro.objects.containing_point(Point(lng, lat))
    except Metro.DoesNotExist:
        raise Http404("Couldn't find any metro matching that query")

    fields = [f.name for f in metro._meta.fields]
    fields.remove('location')
    metro = dict([(f, metro.serializable_value(f)) for f in fields])

    return HttpResponse(json.dumps(metro), mimetype='application/javascript')

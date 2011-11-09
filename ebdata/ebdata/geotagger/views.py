#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

from django.http import HttpResponse
import re
from django.utils import simplejson as json 

from ebdata.nlp.addresses import tag_addresses
from ebdata.nlp.places import place_tagger, location_tagger
from ebpub.geocoder.base import DoesNotExist, full_geocode

def geocode(request): 
    """
    parameters:
    q - query string ostensibly containing a single address 
    or location to be geocoded
    """
    query = request.REQUEST.get('q', '').strip()
    if query:
        try:
            results = _build_geocoder_results(query)
        except:
            results = ()
    else:
        results = ()

    response = {'results': results}
    return HttpResponse(json.dumps(response), mimetype="application/json")

def geotag(request):
    """
    accepts a block of text, extracts addresses, locations 
    and places and geocodes them. 
    """
    # XXX this is very brutal and wacky looking... 
    # it re-uses as much of the existing way of doing things 
    # as possible without regard to time costs or instanity of 
    # interface.  Once this has a more clear form, a more 
    # optimized way of attacking this could be devised if needed.
    
    text = request.REQUEST.get('q', '').strip()
    
    pre = '<geotagger:location>'
    post = '</geotagger:location>'
    text = tag_addresses(text, pre=pre, post=post)
    text = location_tagger(pre=pre, post=post)(text)
    text = place_tagger(pre=pre, post=post)(text)

    all_pat = re.compile('%s(.*?)%s' % (pre, post))
    results = []
    all_locations = []
    for loc in all_pat.findall(text):
        try:
            all_locations.append(loc)
            results += _build_geocoder_results(loc)
        except DoesNotExist:
            pass

    response = {'locations': results, 'searched': all_locations}
    return HttpResponse(json.dumps(response, indent=2),
                        mimetype="application/json")


def _build_geocoder_results(query):
    results = full_geocode(query)
    if results['type'] == 'block':
        return []

    if results['ambiguous'] == True:
        rs = results['result']
    else:
        rs = [results['result']]
        
    return [_build_json_result(query, r, results) for r in rs]

def _build_json_result(query, result, results):

    if results['type'] == 'address': 
        return {
            'query': query,
            'type': 'address',
            'address': result.get('address'),
            'city': result.get('city'),
            'state': result.get('state'),
            'zip': result.get('zip'),
            'latlng': [result.lat, result.lng]
        }
    if results['type'] == 'location':
        return {
            'query': query,
            'type': result.location_type.name,
            'name': result.name,
            'city': result.city,
            'latlng': [result.location.centroid.y, result.location.centroid.x]
        }
    if results['type'] == 'place': 
        return {
            'query': query,
            'type': 'place',
            'name': result.pretty_name,
            'address': result.address, 
            'latlng': [result.location.y, result.location.x]
        }

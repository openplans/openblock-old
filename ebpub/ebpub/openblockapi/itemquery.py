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

"""
Filtering of NewsItems for the openblock REST API.

TODO: This is largely parallel to ebpub.db.schemafilters,
and could be merged with that code?

Filters accept and return:
 * the current django model query
 * the remaining set of parameters describing the query
 * an arbitrary state dictionary for signaling / caching

The first filter to use a parameter removes it.
Related filters can communicate through the 'state' dict.

This allows identification of unused/ill specified parameters and
disallows overlapping interpretations of a parameter.

The full set of parameters that control these filters is specified in
the API documentation.
"""

from django.contrib.gis import geos
from ebpub.utils.dates import parse_date
from ebpub.db.models import NewsItem
from ebpub.streets.models import Place
import pyrfc3339
import re

__all__ = ['build_item_query', 'build_place_query']


class QueryError(Exception):
    def __init__(self, message):
        self.message = message

def build_item_query(request):
    """
    builds a NewsItem QuerySet according to the request parameters given as
    specified in the API documentation.  raises QueryError if
    invalid query parameters are specified.

    Returns the queryset, and a dictionary of *unused* parameters.
    """
    params = _copy_nomulti(request.GET)
    # some different ordering may be more optimal here /
    # some index could be specifically created.
    # Also this could be rewritten to use ebpub.db.schemafilter
    filters = [_schema_filter,
               _id_filter,
               _daterange_filter, _predefined_place_filter,
               _radius_filter, _bbox_filter, _attributes_filter, _order_by,
               _object_limit]

    query = NewsItem.objects.by_request(request)
    params = dict(params)
    state = {}
    for f in filters:
        query, params, state = f(query, params, state)

    return query, params


def _schema_filter(query, params, state):
    """
    handles filtering items by schema type
    parameters: type
    """

    slug = params.pop('type', None)
    if slug is not None:
        if isinstance(slug, basestring):
            query = query.filter(schema__slug=slug)
        else:
            query = query.filter(schema__slug__in=slug)
        state['schema_slug'] = slug
    return query, params, state

def _id_filter(query, params, state):
    """
    handles filtering items by explicit IDs
    parameters: 'id'
    """
    ids = params.pop('id', None)
    if ids is not None:
        if isinstance(ids, basestring):
            ids = [i for i in re.split(r'[^\d]+', ids) if i.strip()]
        if ids:
            query = query.filter(id__in=ids)
    return query, params, state


def _attributes_filter(query, params, state):
    # not implemented yet
    return query, params, state

def _daterange_filter(query, params, state):
    """
    handles filtering by start and end date
    paramters: startdate, enddate
    """
    startdate = params.get('startdate')
    if startdate is not None:
        try:
            del params['startdate']
            try:
                startdate = parse_date(startdate, '%Y-%m-%d')
            except ValueError:
                startdate = pyrfc3339.parse(startdate)
            query = query.filter(pub_date__gte=startdate)
        except ValueError:
            raise QueryError('Invalid start date "%s", must be YYYY-MM-DD or rfc3339' % startdate)
    
    enddate = params.get('enddate')
    if enddate is not None:
        try:
            del params['enddate']
            try:
                enddate = parse_date(enddate, '%Y-%m-%d')
            except ValueError: 
                enddate = pyrfc3339.parse(enddate)
            query = query.filter(pub_date__lte=enddate)
        except ValueError:
            raise QueryError('Invalid end date "%s", must be YYYY-MM-DD or rfc3339' % enddate)

    return query, params, state

def _predefined_place_filter(query, params, state):
    """
    handles filtering by predefined place (newsitemlocation)
    parameters: locationid
    """
    locationid = params.pop('locationid', None)
    if locationid is None: 
        return query, params, state
    if state.get('has_geo_filter') == True: 
        raise QueryError('Only one geographic filter may be specified')

    if isinstance(locationid, basestring):
        ids = [locationid]
    else:
        ids = locationid
    queries = []
    from django.db.models import Q
    # Need to build up an OR query, so we use django Q objects.
    for loc in ids:
        try:
            # Note, API doc specifies splitting on "/" but
            # we also support commas for convenience of ebpub.richmaps
            loctypeslug, locslug = re.split(r'[/,]', loc)
            queries.append(Q(newsitemlocation__location__slug=locslug,
                             newsitemlocation__location__location_type__slug=loctypeslug))
        except ValueError: 
            raise QueryError('Invalid location identifier "%s"' % loc)
    if queries:
        loc_query = queries[0]
        for q in queries[1:]:
            loc_query = loc_query | q

        # Could get overlaps?
        query = query.filter(loc_query).distinct()

    state['has_geo_filter'] = True
    return query, params, state


def _bbox_filter(query, params, state):
    """
    handles filtering by a bounding box region
    parameters: bbox 
    comma separated lon1,lat1,lon2,lat2
    eg bbox=-71.775184936525,42.077772745456,-70.541969604493,42.585381248024
    """
    
    bbox = params.get('bbox')
    if bbox is None: 
        return query, params, state
    
    if state.get('has_geo_filter') == True: 
        raise QueryError('Only one geographic filter may be specified')

    try:
        lon1,lat1,lon2,lat2 = (float(x.strip()) for x in bbox.split(','))
        search_region = geos.Polygon.from_bbox([lon1,lat1,lon2,lat2])
        search_region.srid = 4326
        query = query.filter(location__contained=search_region)
    except:
        import traceback
        traceback.print_exc()
        raise QueryError("Invalid bounding box.")
        
    state['has_geo_filter'] = True
    
    return query, params, state

def _radius_filter(query, params, state):
    """
    handles filtering by a 'circular' geographic region
    parameters: center, radius
    """
    center = params.get('center')
    radius = params.get('radius')
    
    if center is None and radius is None: 
        return query, params, state

    if 'center' in params: 
        del params['center']
    if 'radius' in params: 
        del params['radius']

    if state.get('has_geo_filter') == True: 
        raise QueryError('Only one geographic filter may be specified')

    try: 
        lon, lat = [float(x.strip()) for x in center.split(',')]
        center = geos.Point(lon, lat, srid=4326)
    except ValueError:
        raise QueryError('Invalid center point "%s"' % center)
        
    try:
        radius = float(radius)
        if radius < 0: 
            raise QueryError('Radius must be greater than 0')
        # pop into spherical mercator to make a circle in meters
        search_region = center.transform(3785, True)
        search_region = search_region.buffer(radius)
    except ValueError:
        raise QueryError('Invalid radius "%s"' % radius)

    query = query.filter(location__bboverlaps=search_region)
    state['has_geo_filter'] = True

    return query, params, state

def _object_limit(query, params, state):
    """
    handles limiting the number of results and skipping results
    parameters: limit, offset
    """
    try: 
        offset = int(params.get('offset', 0))
    except:
        raise QueryError('Invalid offset')
    
    try: 
        limit = int(params.get('limit', 50))
        if limit > 1000: 
            limit = 1000
    except:
        raise QueryError('Invalid limit')
    
    if 'limit' in params: 
        del params['limit']
    if 'offset' in params: 
        del params['offset']

    query = query[offset:offset+limit]
    
    return query, params, state

def _order_by(query, params, state):
    """
    handles order of results.
    parameters: None, currently fixed
    """
    # it is always by item date currently
    query = query.order_by('-item_date')
    return query, params, state


###################################
# Some piggy-backing for Places API
###################################

def _placetype_filter(query, params, state):
    """
    handles filtering Places by placetype
    """
    query = query.filter(place_type__is_mappable=True)

    slug = params.get('type')
    if slug is not None:
        del params['type']
        state['placetype_slug'] = slug
        query = query.filter(place_type__slug=slug)    
    return query, params, state


def build_place_query(params):
    """
    builds a Place QuerySet according to the request parameters given 
    as specified in the API documentation. raises QueryError if 
    invalid query parameters are specified. 
    """
    filters = [_placetype_filter, _radius_filter, _bbox_filter, _object_limit]

    query = Place.objects.all()
    params = dict(params)
    state = {}
    for f in filters: 
        query, params, state = f(query, params, state)

    return query, params

def _copy_nomulti(d):
    """
    make a copy of django wack-o immutable query multi-dict
    making single item values non-lists.
    """
    d = dict(d) # Work around request.GET.items() not giving all values
    r = {}
    for k,v in d.items():
        try:
            if len(v) == 1:
                r[k] = v[0]
            else:
                r[k] = v
        except TypeError:
            r[k] = v
    return r

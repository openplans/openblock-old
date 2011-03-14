from django.contrib.gis import geos
from ebpub.db.models import NewsItem, Schema
import datetime
import pyrfc3339

__all__ = ['build_item_query']


class QueryError(object):
    def __init__(message):
        self.message = message

def build_item_query(params):
    """
    builds a NewsItem QuerySet according to the request parameters given as
    specified in the API documentation.  raises QueryError if 
    invalid query parameters are specified.
    """
    
    # some different ordering may be more optimal here /
    # some index could be specifically created
    filters = [_schema_filter, _daterange_filter, _predefined_place_filter,
               _radius_filter, _attributes_filter, _order_by, _object_limit]

    query = NewsItem.objects.all()
    params = dict(params)
    state = {}
    for f in filters: 
        query, params, state = f(query, params, state)

    return query, params

# 
# filters accept and return:
# * the current django model query
# * the remaining set of parameters describing the query 
# * an arbitrary state dictionary for signaling / caching
# 
# the first filter to use a parameter removes it.
# related filters can communicate through 'state' 
#
# this allows identification of unused/ill specified 
# parameters and disallows overlapping interpretations of 
# a parameter.
#
# The full set of parameters that control these filters
# is specified in the API documentation.
#

def _schema_filter(query, params, state):
    """
    handles filtering items by schema type
    parameters: type
    """

    # always filter out items with non-public schema
    query = query.filter(schema__is_public=True)

    slug = params.get('type')
    if slug is not None:
        del params['type']
        state['schema_slug'] = slug
        query = query.filter(schema__slug=slug)    
    return query, params, state

def _attributes_filter(query, params, state):
    # not implemented yet
    #
    # schema_slug = state.get('schema_slug')
    # if schema_slug is None or len(params) == 0: 
    #     return query, params, state
        
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
                startdate = datetime.datetime.strptime(startdate, '%Y-%m-%d')
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
                enddate = datetime.datetime.strptime(enddate, '%Y-%m-%d')
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
    locationid = params.get('locationid')
    if locationid is None: 
        return query, params, state
        
    del params['locationid']
    
    if state.get('has_geo_filter') == True: 
        raise QueryError('Only one geographic filter may be specified')

    try:
        loctypeslug, locslug = locationid.split('/')
        query = query.filter(newsitemlocation__location__slug=locslug,
                             newsitemlocation__location__location_type__slug=loctypeslug) 
    except ValueError: 
        raise QueryError('Invalid location identifier "%s"' % locationid)

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
        raise Queryerror('Invalid center point "%s"' % center)
        
    try:
        radius = float(radius)
        if radius < 0: 
            raise QueryError('Radius must be greater than 0')
        # pop into spherical mercator to make a circle in meters
        search_region = center.transform(3785, True)
        search_region = search_region.buffer(radius)
    except ValueError:
        raise QueryError('Invalid radius "%s"' % radius)

    search_buffer = None
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
        limit = int(params.get('limit', 25))
        if limit > 200: 
            limit = 200
    except:
        raise QueryError(400, 'Invalid limit')
    
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

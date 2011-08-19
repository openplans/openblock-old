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

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import feedgenerator
from django.utils import simplejson
from django.utils.cache import patch_response_headers
from ebpub.db import models
from ebpub.geocoder import DoesNotExist
from ebpub.openblockapi.itemquery import build_item_query, build_place_query, QueryError
from .apikey.auth import KEY_HEADER
from .apikey.auth import check_api_authorization
from ebpub.streets.models import PlaceType
from ebpub.streets.utils import full_geocode
from ebpub.utils.dates import parse_date, parse_time
from ebpub.utils.geodjango import ensure_valid
from functools import wraps
import copy
import datetime
import logging
import pyrfc3339
import pytz
import re

JSONP_QUERY_PARAM = 'jsonp'
ATOM_CONTENT_TYPE = "application/atom+xml"
JSON_CONTENT_TYPE = 'application/json'
JAVASCRIPT_CONTENT_TYPE = 'application/javascript'

LOCAL_TZ = pytz.timezone(settings.TIME_ZONE)

logger = logging.getLogger('openblockapi')

############################################################
# Util functions.
############################################################

def APIGETResponse(request, body, **kw):
    """
    constructs either a normal HTTPResponse using the
    keyword arguments given or a JSONP / JSONPX wrapped response
    depending on the presence and validity of
    JSONP_QUERY_PARAM in the request.

    This may alter the content type of the response
    if JSONP/JSONPX is triggered. Status is preserved.
    """
    jsonp = request.GET.get(JSONP_QUERY_PARAM)
    format = kw.setdefault('content_type', JSON_CONTENT_TYPE)
    if format == JSON_CONTENT_TYPE and not isinstance(body, basestring):
        body = simplejson.dumps(body, indent=1, default=_serialize_unknown)
    if jsonp is None:
        return HttpResponse(body, **kw)
    else:
        jsonp = re.sub(r'[^a-zA-Z0-9_]+', '', jsonp)
        body = '%s(%s);' % (jsonp, body)
        kw['content_type'] = JAVASCRIPT_CONTENT_TYPE
        return HttpResponse(body, **kw)

def normalize_datetime(dt):
    # XXX needs tests
    if dt.tzinfo is None:
        # Assume naive times are in local zone.
        dt = dt.replace(tzinfo=LOCAL_TZ)
    return dt.astimezone(LOCAL_TZ)

def get_datatype(schemafield):
    """
    Human-readable datatype based on real_name; notably, use 'text',
    not 'varchar'; Lookups are 'text'.
    """
    if schemafield.is_lookup:
        datatype = 'text'
    else:
        datatype = schemafield.datatype
        if datatype == 'varchar':
            datatype = 'text'
    return datatype

def _copy_nomulti(d):
    """
    make a copy of django wack-o immutable query mulit-dict
    making single item values non-lists.
    """
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

def api_items_geojson(items):
    """
    helper to produce the geojson of the same form as the 
    API in other contexts (not a view)
    """
    body = {'type': 'FeatureCollection',
            'features': [item for item in items if item.location]}
    return simplejson.dumps(body, indent=1, default=_serialize_unknown)

def _item_geojson_dict(item):
    # Prepare a single NewsItem as a structure that can be JSON-encoded.
    props = {}
    geom = simplejson.loads(item.location.geojson)
    result = {
        'type': 'Feature',
        'geometry': geom,
        }
    for attr in item.attributes_for_template():
        key = attr.sf.name
        if attr.sf.is_many_to_many_lookup():
            props[key] = attr.values
        else:
            props[key] = attr.values[0]

    props.update(
        {'type': item.schema.slug,
         'title': item.title,
         'description': item.description,
         'url': item.url,
         'pub_date': item.pub_date,
         'item_date': item.item_date,
         'id': item.id,
         'openblock_type': 'newsitem',
         'icon': item.schema.map_icon_url,
         'color': item.schema.map_color,
         'location_name': item.location_name,
         })
    result['properties'] = props
    return result

def is_instance_of_model(obj, model):
    # isinstance(foo, model) seems to work *sometimes* with django models,
    # but not always; no idea what's going on there.
    # This should always work.
    return (isinstance(obj, model)
            or type(obj) is model
            or model in obj.__class__.__bases__)

def _serialize_unknown(obj):
    # Handle NewsItems and various other types that default json serializer
    # doesn't know how to do.
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return serialize_date_or_time(obj)
    elif is_instance_of_model(obj, models.Lookup):
        return obj.name
    elif is_instance_of_model(obj, models.NewsItem):
        return _item_geojson_dict(obj)
    return None

def serialize_date_or_time(obj):
    if isinstance(obj, datetime.datetime):
        obj = normalize_datetime(obj)
        return pyrfc3339.generate(obj, utc=False)
    elif isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, datetime.time):
        # XXX super ugly
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=LOCAL_TZ)
        dd = datetime.datetime.now()
        dd = dd.replace(hour=obj.hour, minute=obj.minute,
                        second=obj.second, tzinfo=obj.tzinfo)
        dd = normalize_datetime(dd)
        ss = pyrfc3339.generate(dd, utc=False)
        return ss.split('T', 1)[1]
    else:
        return None

def _get_location_info(geometry, location_name):
    location = None
    if geometry:
        # geometry is a decoded geojson geometry dict.
        # GEOSGeometry can already parse geojson geometries (as a string)...
        # but not the whole geojson string... so we have to re-encode
        # just the geometry :-P
        from django.contrib.gis.geos import GEOSGeometry
        location = GEOSGeometry(simplejson.dumps(geometry))
        location = ensure_valid(location)
        if not location_name:
            raise NotImplementedError("Should do reverse-geocoding here")
    elif location_name:
        raise NotImplementedError("Should do geocoding here.")
    return location, location_name

def rest_view(methods, cache_timeout=None):
    """
    Decorator that applies throttling and restricts the available HTTP
    methods, and optionally adds some HTTP cache headers based on cache_timeout.
    """
    def inner(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return HttpResponseNotAllowed(methods)
            seconds_throttled = throttle_check(request)
            if seconds_throttled > 0:
                msg = u'Throttle limit exceeded. Try again in %d seconds.\n' % seconds_throttled
                response = HttpResponse(msg, status=503)
                response['Retry-After'] = str(seconds_throttled)
                response['Content-Type'] = 'text/plain'
                return response
            response = func(request, *args, **kwargs)
            if cache_timeout is not None:
                patch_response_headers(response, cache_timeout=cache_timeout)
            return response

        return wrapper
    return inner

from ebpub.openblockapi.throttle import CacheThrottle


# We could have more than one throttle instance to be more flexible.
_throttle = CacheThrottle(
    throttle_at=getattr(settings, 'API_THROTTLE_AT', 150), # max requests per timeframe.
    timeframe=getattr(settings, 'API_THROTTLE_TIMEFRAME', 60 * 60), # default 1 hour.
    expiration=getattr(settings, 'API_THROTTLE_EXPIRATION', 60 * 60 * 24 * 7)  # default 1 week.
    )

def throttle_check(request):
    """
    Handles checking if the request should be throttled.

    If so, returns number of seconds after which user can try again.
    If not, returns 0.

    Based originally on code from TastyPie, copyright Daniel Lindsley,
    BSD license.
    """
    
    # First get best user identifier available.
    if request.user.is_authenticated():
        identifier = request.user.username
    elif request.META.get(KEY_HEADER, None) is not None:
        identifier = request.META[KEY_HEADER]
    else:
        identifier = "%s_%s" % (request.META.get('REMOTE_ADDR', 'noaddr'),
                                request.META.get('REMOTE_HOST', 'nohost'))

    if _throttle.should_be_throttled(identifier):
        # Throttle limit exceeded.
        return _throttle.seconds_till_unthrottling(identifier)

    # Log throttle access.
    _throttle.accessed(identifier, url=request.get_full_path(),
                      request_method=request.method.lower())
    return 0


class HttpResponseCreated(HttpResponseRedirect):
    status_code = 201

class HttpResponseUnavailable(HttpResponse):
    status_code = 503

############################################################
# View functions.
############################################################

@rest_view(['GET'], cache_timeout = 7 * 24 * 60 * 60)
def check_api_available(request):
    """
    endpoint to indicate that this version of the API
    is available.
    """
    return HttpResponse(status=200)

@rest_view(['GET'], cache_timeout=3600)
def items_json(request):
    """
    handles the items.json API endpoint
    """
    # TODO: support filtering by block + radius, and somehow support
    # adding extra info eg. popup html.  Together, that would allow
    # this to replace ebub.db.views.newsitems_geojson. See #81
    try:
        items, params = build_item_query(_copy_nomulti(request.GET))
        # could test for extra params aside from jsonp...
        items = [item for item in items if item.location is not None]
        items_geojson_dict = {'type': 'FeatureCollection',
                              'features': items
                              }
        return APIGETResponse(request, items_geojson_dict, content_type=JSON_CONTENT_TYPE)
    except QueryError as err:
        return HttpResponseBadRequest(err.message)

@rest_view(['GET'])
def items_atom(request):
    """
    handles the items.atom API endpoint
    """
    try:
        items, params = build_item_query(_copy_nomulti(request.GET))
        # could test for extra params aside from jsonp...
        return APIGETResponse(request, _items_atom(items), content_type=ATOM_CONTENT_TYPE)
    except QueryError as err:
        return HttpResponseBadRequest(err.message)

@rest_view(['GET', 'POST'])
def items_index(request):
    """
    GET: Redirects to a list of JSON items.

    POST: Takes a single JSON mapping describing a NewsItem, creates
    it, and redirects to a JSON view of the created item
    (HTTP response 201).

    On errors, gives a 400 response.

    """
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('items_json'))
    elif request.method == 'POST':
        check_api_authorization(request)
        info = simplejson.loads(request.raw_post_data)
        try:
            item = _item_create(info)
        except InvalidNewsItem, e:
            errors = simplejson.dumps({'errors': e.errors}, indent=2)
            return HttpResponseBadRequest(errors, content_type=JSON_CONTENT_TYPE)
        item_url = reverse('single_item_json', kwargs={'id_': str(item.id)})
        return HttpResponseCreated(item_url)


class InvalidNewsItem(Exception):
    def __init__(self, errors):
        self.errors = errors

#@permission_required('db.add_newsitem')
def _item_create(info):
    info = copy.deepcopy(info)
    try:
        assert info.pop('type') == 'Feature'
        props = info['properties']
    except (KeyError, AssertionError):
        raise InvalidNewsItem({'type': 'not a valid GeoJSON Feature'})
    try:
        slug = props.pop('type', None)
        schema = models.Schema.objects.get(slug=slug)
    except (models.Schema.DoesNotExist):
        raise InvalidNewsItem({'type': 'schema %r does not exist' % slug})

    data = {'schema': schema.id}
    for key in ('title', 'description', 'url'):
        data[key] = props.pop(key, '')

    # If there are errors parsing the dates, keep the raw data and let
    # the ModelForm sort it out.
    pub_date = props.pop('pub_date', None)
    if pub_date:
        try:
            data['pub_date'] = normalize_datetime(pyrfc3339.parse(pub_date))
        except Exception:
            data['pub_date'] = pub_date
    else:
        data['pub_date'] = normalize_datetime(datetime.datetime.utcnow())
    item_date = props.pop('item_date', None)
    if item_date:
        try:
            data['item_date'] = parse_date(item_date, '%Y-%m-%d', False)
        except Exception:
            data['item_date'] = item_date
    else:
        try:
            data['item_date'] = data['pub_date'].date()
        except Exception:
            data['item_date'] = None

    data['location'], data['location_name'] = _get_location_info(
        info.get('geometry'), props.pop('location_name', None))
    if not data['location']:
        logger.warn("Saving NewsItem %s with no geometry" % data['title'])
    if not data['location_name']:
        logger.warn("Saving NewsItem %s with no location_name" % data['title'])


    from ebpub.db.forms import NewsItemForm
    form = NewsItemForm(data)
    if form.is_valid():
        item = form.save()
    else:
        raise InvalidNewsItem(form.errors)

    # Everything else goes in .attributes.
    attributes = {}
    for key, val in props.items():
        sf = models.SchemaField.objects.get(schema=schema, name=key)
        if sf.is_many_to_many_lookup():
            lookups = []
            for lookup_name in val:
                lookups.append(
                    models.Lookup.objects.get_or_create_lookup(sf, lookup_name))
            val = ','.join((str(lookup.id) for lookup in lookups))
        elif sf.is_lookup:
            val = models.Lookup.objects.get_or_create_lookup(sf, val)
        elif sf.is_type('date'):
            val = normalize_datetime(parse_date(val, '%Y-%m-%d'))
        elif sf.is_type('time'):
            val = normalize_datetime(parse_time(val, '%H:%M'))
        elif sf.is_type('datetime'):
            val = normalize_datetime(pyrfc3339.parse(datetime))
        attributes[key] = val
    item.attributes = attributes
    return item


@rest_view(['GET'], cache_timeout=3600)
def single_item_json(request, id_=None):
    """
    GET a single item as GeoJSON.
    """
    assert request.method == 'GET'
    # TODO: handle PUT, DELETE?
    from ebpub.db.models import NewsItem
    item = get_object_or_404(NewsItem.objects.select_related(), pk=id_)
    return APIGETResponse(request, item, content_type=JSON_CONTENT_TYPE)



def _items_atom(items):
    # XXX needs tests
    feed_url = reverse('items_atom')
    atom = OpenblockAtomFeed(
        title='openblock news item atom feed', description='',
        link=reverse('items_json'),  # For the rel=alternate link.
        feed_url=feed_url,
        id=feed_url,)

    for item in items:
        location = item.location
        if location:
            location = location.centroid
        attributes = []
        for attr in item.attributes_for_template():
            datatype = get_datatype(attr.sf)
            for val in attr.values:
                if attr.sf.is_lookup:
                    val = val.name
                attributes.append((attr.sf.name, datatype, val))
        atom.add_item(item.title,
                      item.url, # XXX should this be a local url?
                      item.description,
                      location=location,
                      location_name=item.location_name,
                      pubdate=normalize_datetime(item.pub_date),
                      schema_slug=item.schema.slug,
                      attributes=attributes,
                      )

    return atom.writeString('utf8')


@rest_view(['GET'], cache_timeout=3600)
def geocode(request):
    # TODO: this will obsolete:
    # ebdata.geotagger.views.geocode and 
    # ebpub.db.views.ajax_wkt
    q = request.GET.get('q', '').strip()
    if not q:
        return HttpResponseBadRequest('Missing or empty q parameter.')
    collection = {'type': 'FeatureCollection',
                  'features': _geocode_geojson(q)}
    if collection['features']:
        status = 200
    else:
        status = 404
    return APIGETResponse(request, simplejson.dumps(collection, indent=1),
                          content_type=JSON_CONTENT_TYPE, status=status)

def _geocode_geojson(query):
    if not query: 
        return []
        
    try: 
        res = full_geocode(query)
        # normalize a bit
        if not res['ambiguous']: 
            res['result'] = [res['result']]
    except DoesNotExist:
        return []
        
    features = []
    if res['type'] == 'location':
        for r in res['result']: 
            feature = {
                'type': 'Feature',
                'geometry': simplejson.loads(r.location.centroid.geojson),
                'properties': {
                    'type': r.location_type.slug,
                    'name': r.name,
                    'city': r.city,
                    'query': query,
                }
            }
            features.append(feature)
    elif res['type'] == 'place':
        for r in res['result']: 
            feature = {
                'type': 'Feature',
                'geometry': simplejson.loads(r.location.geojson),
                'properties': {
                    'type': 'place',
                    'name': r.pretty_name,
                    'address': r.address, 
                    'query': query,
                }
            }
            features.append(feature)
    elif res['type'] == 'address':
        for r in res['result']:
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [r.lng, r.lat],
                },
                'properties': {
                    'type': 'address',
                    'address': r.get('address'),
                    'city': r.get('city'),
                    'state': r.get('state'),
                    'zip': r.get('zip'),
                    'query': query
                }
            }
            features.append(feature)
    # we could get type == 'block', but 
    # ebpub.db.views.ajax_wkt returned nothing for this,
    # so for now we follow their lead.
    # elif res['type'] == 'block': 
    #     pass

    return features

@rest_view(['GET'], cache_timeout = 24 * 3600)
def list_types_json(request):
    """
    List the known NewsItem types (Schemas).
    """
    schemas = {}
    for schema in models.Schema.public_objects.all():
        attributes = {}
        for sf in schema.schemafield_set.all():
            fieldtype = get_datatype(sf)
            attributes[sf.name] = {
                'pretty_name': sf.smart_pretty_name(),
                'type': fieldtype,
                # TODO: what else?
                }
            # TODO: should we enumerate known values of Lookups?
        schemas[schema.slug] = {
                'indefinite_article': schema.indefinite_article,
                'last_updated': schema.last_updated.strftime('%Y-%m-%d'),
                'name': schema.name,
                'plural_name': schema.plural_name,
                'slug': schema.slug,
                'attributes': attributes,
                }

    return APIGETResponse(request, simplejson.dumps(schemas, indent=1),
                          content_type=JSON_CONTENT_TYPE)

@rest_view(['GET'], cache_timeout=24 * 3600)
def locations_json(request):
    locations = models.Location.objects.filter(is_public=True)
    loctype = request.GET.get('type')
    if loctype is not None:
        locations = locations.filter(location_type__slug=loctype)

    locations = locations.order_by('display_order').select_related().defer('location')
    
    loc_objs = [
        {'id': "%s/%s" % (loc.location_type.slug, loc.slug),
         'slug': loc.slug, 'name': loc.name, 'city': loc.city,
         'type': loc.location_type.slug,
         'description': loc.description or '',
         'url': reverse('location_detail_json', kwargs={'slug': loc.slug, 'loctype': loc.location_type.slug})
         }
        for loc in locations]

    return APIGETResponse(request, simplejson.dumps(loc_objs, indent=1),
                          content_type=JSON_CONTENT_TYPE)

@rest_view(['GET'], cache_timeout=24 * 3600)
def location_detail_json(request, loctype, slug):
    # TODO: this will obsolete ebpub.db.views.ajax_location
    try:
        loctype_obj = models.LocationType.objects.get(slug=loctype)
    except (ValueError, models.LocationType.DoesNotExist):
        raise Http404("No such location type %r" % loctype)
    try:
        location = models.Location.objects.geojson().get(
            location_type=loctype_obj, slug=slug)
    except (ValueError, models.Location.DoesNotExist):
        raise Http404("No such location %r/%r" % (loctype, slug))
    geojson = {'type': 'Feature',
               'id': '%s/%s' % (loctype, slug),
               'geometry': simplejson.loads(location.geojson),
               'properties': {'type': loctype,
                              'slug': location.slug,
                              'source': location.source,
                              'description': location.description,
                              'centroid': location.location.centroid.wkt,
                              'area': location.area,
                              'population': location.population,
                              'city': location.city,
                              'name': location.name,
                              'openblock_type': 'location',
                              }
               }
    geojson = simplejson.dumps(geojson, indent=1)
    return APIGETResponse(request, geojson, content_type=JSON_CONTENT_TYPE)

@rest_view(['GET'], cache_timeout = 24 * 3600)
def location_types_json(request):
    typelist = models.LocationType.objects.order_by('plural_name').values(
        'name', 'plural_name', 'scope', 'slug')
    typedict = {}
    for typeinfo in typelist:
        typedict[typeinfo.pop('slug')] = typeinfo

    return APIGETResponse(request, simplejson.dumps(typedict, indent=1),
                         content_type=JSON_CONTENT_TYPE)


@rest_view(['GET'], cache_timeout = 24 * 3600)
def place_types_json(request):
    typelist = PlaceType.objects.filter(is_mappable=True).order_by('plural_name').values(
        'name', 'plural_name', 'slug')
    typedict = {}
    for typeinfo in typelist: 
        slug = typeinfo.pop('slug')
        typedict[slug] = typeinfo
        typedict[slug]['geojson_url'] = reverse('place_detail_json', kwargs={'placetype': slug})

    return APIGETResponse(request, simplejson.dumps(typedict, indent=1),
                         content_type=JSON_CONTENT_TYPE)

@rest_view(['GET'], cache_timeout = 24 * 3600)
def place_detail_json(request, placetype):
    try:
        placetype_obj = PlaceType.objects.get(slug=placetype, is_mappable=True)
    except (ValueError, PlaceType.DoesNotExist):
        raise Http404("No mappable place type %r" % placetype)

    result = {
        'type': 'FeatureCollection',
        'features': []
    }
    
    params = _copy_nomulti(request.GET)
    params['type'] = placetype
    places, params = build_place_query(params)
    for place in places:
        feature = {'type': 'Feature',
                   'geometry': simplejson.loads(place.location.geojson),
                   'properties': {'type': placetype,
                                  'name': place.pretty_name,
                                  'address': place.address,
                                  'icon': place.place_type.map_icon_url,
                                  'color': place.place_type.map_color,
                                  'id': place.id,
                                  'openblock_type': 'place'
                                  }
                   }
        result['features'].append(feature)

    geojson = simplejson.dumps(result, indent=1)
    return APIGETResponse(request, geojson, content_type=JSON_CONTENT_TYPE)


class OpenblockAtomFeed(feedgenerator.Atom1Feed):
    """
    An Atom feed generator that adds extra stuff like georss.
    """

    def root_attributes(self):
        attrs = super(OpenblockAtomFeed, self).root_attributes()
        attrs['xmlns:georss'] = 'http://www.georss.org/georss'
        attrs['xmlns:openblock'] = 'http://openblock.org/ns/0'
        return attrs

    def add_item_elements(self, handler, item):
        super(OpenblockAtomFeed, self).add_item_elements(handler, item)
        location = item['location']
        if location is not None:
            # yes, georss is "y x" not "x y"!!
            handler.addQuickElement('georss:point', '%.16f %.16f' % (location.y, location.x))
        handler.addQuickElement('georss:featureName', item['location_name'])

        handler.addQuickElement('openblock:type', item['schema_slug'])

        # TODO: item_date in custom namespace
        handler.startElement(u'openblock:attributes', {})
        for key, datatype, val in item['attributes']:
            val = serialize_date_or_time(val) or val
            handler.addQuickElement('openblock:attribute', unicode(val),
                                    {'name': key, 'type': datatype})
        handler.endElement(u'openblock:attributes')

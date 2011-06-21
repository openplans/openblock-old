from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import feedgenerator
from django.utils import simplejson
from ebpub.db import models
from ebpub.geocoder import DoesNotExist
from ebpub.openblockapi.itemquery import build_item_query, QueryError
from ebpub.streets.models import PlaceType, Place, PlaceSynonym
from ebpub.streets.utils import full_geocode
from ebpub.utils.dates import parse_date, parse_time
from ebpub.utils.geodjango import ensure_valid
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

def _item_geojson_dict(item):
    props = {}
    geom = simplejson.loads(item.location.geojson)
    result = {
        # 'id': i.id, # XXX ?
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


############################################################
# View functions.
############################################################

def check_api_available(request):
    """
    endpoint to indicate that this version of the API
    is available.
    """
    return HttpResponse(status=200)


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
        return HttpResponse(err.message, status=400)

def items_atom(request):
    """
    handles the items.atom API endpoint
    """
    try:
        items, params = build_item_query(_copy_nomulti(request.GET))
        # could test for extra params aside from jsonp...
        return APIGETResponse(request, _items_atom(items), content_type=ATOM_CONTENT_TYPE)
    except QueryError as err:
        return HttpResponse(err.message, status=400)

def items_index(request):
    """
    GET: Redirects to a list of JSON items.

    POST: Takes a single JSON mapping describing a NewsItem, creates
    it, and redirects to a JSON view of the created item.
    *Temporarily disabled until we have authorization in place*

    On errors, gives a 400 response.

    TODO: documentation in docs/
    """
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('items_json'))
    # elif request.method == 'POST':
    #     return _item_post(request)
    else:
        # return HttpResponseNotAllowed(['GET', 'POST'])
        return HttpResponseNotAllowed(['GET'])

#@permission_required('db.add_newsitem')
def _item_post(request):
    assert request.method == 'POST'
    info = simplejson.loads(request.raw_post_data)
    assert info.pop('type') == 'Feature'
    props = info['properties']
    schema = get_object_or_404(models.Schema.objects, slug=props.pop('type'))
    kwargs = {'schema': schema}
    for key in ('title', 'description', 'url'):
        kwargs[key] = props.pop(key, '')
    item = models.NewsItem(**kwargs)
    item.pub_date =  normalize_datetime(datetime.datetime.utcnow())
    item_date = props.pop('item_date', None)
    if item_date:
        item.item_date = parse_date(item_date, '%Y-%m-%d', False)
    else:
        item.item_date = item.pub_date.date()
    item.location, item.location_name = _get_location_info(
        info.get('geometry'), props.pop('location_name', None))
    if not item.location:
        logger.warn("Saving NewsItem %s with no geometry" % item)
    if not item.location_name:
        logger.warn("Saving NewsItem %s with no location_name" % item)
    item.save()
    # Everything else goes in .attributes.
    attributes = {}
    for key, val in props.items():
        sf = models.SchemaField.objects.get(schema=schema, name=key)
        if sf.is_many_to_many_lookup():
            # TODO: get or create Lookups as needed
            pass
        elif sf.is_lookup:
            # likewise TODO.
            pass
        elif sf.is_type('date'):
            val = normalize_datetime(parse_date(val, '%Y-%m-%d'))
        elif sf.is_type('time'):
            val = normalize_datetime(parse_time(val, '%H:%M'))
        elif sf.is_type('datetime'):
            val = normalize_datetime(pyrfc3339.parse(datetime))
        attributes[key] = val

    item.attributes = attributes
    item_id = str(item.id)
    created = HttpResponse(status=201)
    created['location'] = reverse('single_item_json', kwargs={'id_': item_id})
    return created


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
                'geometry': simplejson.loads(r.centroid.geojson),
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
                    'coordinates': [r.lat, r.lng],
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
                              'centroid': (location.centroid or location.location.centroid).wkt,
                              'area': location.area,
                              'population': location.population,
                              'city': location.city,
                              'name': location.name,
                              }
               }
    geojson = simplejson.dumps(geojson, indent=1)
    return APIGETResponse(request, geojson, content_type=JSON_CONTENT_TYPE)

def location_types_json(request):
    typelist = models.LocationType.objects.order_by('plural_name').values(
        'name', 'plural_name', 'scope', 'slug')
    typedict = {}
    for typeinfo in typelist:
        typedict[typeinfo.pop('slug')] = typeinfo

    return APIGETResponse(request, simplejson.dumps(typedict, indent=1),
                         content_type=JSON_CONTENT_TYPE)


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

def place_detail_json(request, placetype):
    try:
        placetype_obj = PlaceType.objects.get(slug=placetype)
    except (ValueError, PlaceType.DoesNotExist):
        raise Http404("No such place type %r" % placetype)

    result = {
        'type': 'FeatureCollection',
        'features': []
    }
    for place in Place.objects.filter(place_type=placetype_obj):
        feature = {'type': 'Feature',
                   'geometry': simplejson.loads(place.location.geojson),
                   'properties': {'type': placetype,
                                  'name': place.pretty_name,
                                  'address': place.address,
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

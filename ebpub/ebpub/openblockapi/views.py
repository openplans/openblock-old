from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.utils import simplejson
from django.utils import feedgenerator
from ebpub.db import models
from ebpub.geocoder.base import DoesNotExist
from ebpub.openblockapi.itemquery import build_item_query, QueryError
from ebpub.streets.utils import full_geocode
import datetime
import pyrfc3339
import pytz

JSONP_QUERY_PARAM = 'jsonp'
ATOM_CONTENT_TYPE = "application/atom+xml"
JSON_CONTENT_TYPE = 'application/json'
JAVASCRIPT_CONTENT_TYPE = 'application/javascript'



def APIGETResponse(request, body, **kw):
    """
    constructs either a normal HTTPResponse using the 
    keyword arguments given or a JSONP wrapped response
    depending on the presence and validity of 
    JSONP_QUERY_PARAM in the request. 
    
    This may alter the content type of the response 
    if JSONP/JSONPX is triggered. Status is preserved.
    """
    jsonp = request.GET.get(JSONP_QUERY_PARAM)
    if jsonp is None: 
        return HttpResponse(body, **kw)
    else: 
        content_type = kw.get("mimetype", kw.get("content_type", "text/plain"))
        if content_type in (JSON_CONTENT_TYPE, ATOM_CONTENT_TYPE):
            body = jsonp + "(" + body + ");" 
        else: 
            body = jsonp + "(" + simplejson.dumps(body, indent=1) + ");"
        if 'content_type' in kw:
            del kw['content_type']
        if 'mimetype' in kw:
            del kw['mimetype']
        kw['content_type'] = JAVASCRIPT_CONTENT_TYPE
        return HttpResponse(body, **kw)


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
    try:
        items, params = build_item_query(_copy_nomulti(request.GET))
        # could test for extra params aside from jsonp...
        return APIGETResponse(request, _items_json(items), content_type=JSON_CONTENT_TYPE)
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

def _copy_nomulti(d):
    """
    make a copy of django wack-o immutable query mulit-dict
    making single item values non-lists.
    """
    r = {}
    for k,v in d.items():
        if len(v) == 1:
            r[k] = v[0]
        else: 
            r[k] = v
    return r

def _items_json(items):
    result = {
        'type': 'FeatureCollection',
        'features': []
    }
    for i in items:
        if i.location is None: 
            continue
        geom = simplejson.loads(i.location.geojson)
        item = {
            # 'id': i.id, # XXX ?
            'type': 'Feature',
            'geometry': geom,
        }
        props = {}
        for k,v in i.attributes.items():
            props[k] = v
        props.update({
            'type': i.schema.slug,
            'title': i.title,
            'description': i.description,
            'url': i.url,
            'pub_date': pyrfc3339.generate(normalize_datetime(i.pub_date)),
            'item_date': i.item_date,
        })
        item['properties'] = props
        result['features'].append(item)

    local_tz = pytz.timezone(settings.TIME_ZONE)
    def _serialize_unknown(obj):
        if isinstance(obj, datetime.datetime):
            if obj.tzinfo is None:
                obj = obj.replace(tzinfo=local_tz)
            return pyrfc3339.generate(obj)
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            # XXX super ugly
            if obj.tzinfo is None: 
                obj = obj.replace(tzinfo=local_tz)
            dd = datetime.datetime.utcnow()
            dd = dd.replace(hour=obj.hour, minute=obj.minute,
                            second=obj.second, tzinfo=obj.tzinfo)
            ss = pyrfc3339.generate(dd)
            return ss[ss.index('T') + 1:]
    return simplejson.dumps(result, default=_serialize_unknown, indent=1)


def _items_atom(items):
    feed_url = reverse('items_atom')
    atom = OpenblockAtomFeed(
        title='openblock news item atom feed', description='xxx descr',
        link=reverse('items_json'),
        feed_url=feed_url,
        id=feed_url,)

    for item in items:
        location = item.location
        if location:
            location = location.centroid

        atom.add_item(item.title,
                      item.url, # XXX should this be a local url?
                      item.description,
                      location=location,
                      location_name=item.location_name,
                      pubdate=normalize_datetime(item.pub_date),
                      schema_slug=item.schema.slug,
                      )

    return atom.writeString('utf8')



def geocode(request):
    # TODO: this will obsolete:
    # ebdata.geotagger.views.geocode and 
    # ebpub.db.views.ajax_wkt

    q = request.GET.get('q', '').strip()
                
    collection = {'type': 'FeatureCollection',
                  'features': _geocode_geojson(q)}
    return APIGETResponse(request, simplejson.dumps(collection, indent=1), mimetype="application/json")

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
    # ebpub.db.views returns nothing for this,
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
            if sf.is_lookup:
                fieldtype = 'text'
            else:
                fieldtype = sf.datatype
                if fieldtype == 'varchar':
                    fieldtype = 'text'
            attributes[sf.slug] = {
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
                          content_type='application/json')

def locations_json(request):
    # TODO: this will obsolete ebpub.db.views.ajax_location_list
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
                          content_type='application/json')

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
    return APIGETResponse(request, geojson, content_type='application/json')

def location_types_json(request):
    typelist = models.LocationType.objects.order_by('name').values(
        'name', 'plural_name', 'scope', 'slug')
    typedict = {}
    for typeinfo in typelist:
        typedict[typeinfo.pop('slug')] = typeinfo

    return APIGETResponse(request, simplejson.dumps(typedict, indent=1),
                         content_type='application_json')


class OpenblockAtomFeed(feedgenerator.Atom1Feed):

    """
    An Atom feed generator that adds extra stuff like georss.
    """
    def root_attributes(self):
        attrs = super(OpenblockAtomFeed, self).root_attributes()
        attrs['xmlns:georss'] = 'http://www.georss.org/georss'
        return attrs

    def add_item_elements(self, handler, item):
        super(OpenblockAtomFeed, self).add_item_elements(handler, item)
        location = item['location']
        if location is not None:
            # yes, georss is "y x" not "x y"!!
            handler.addQuickElement('georss:point', '%s %s' % (location.y, location.x))
        handler.addQuickElement('georss:featureName', item['location_name'])
        typeinfo = {'term': item['schema_slug'],
                    'scheme': 'http://openblockproject.org/schema' # XXX  what should this be?
                    }
        handler.addQuickElement('category', u"", typeinfo)

        # TODO: item_date


def normalize_datetime(dt):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=local_tz)
    return dt.astimezone(pytz.utc)


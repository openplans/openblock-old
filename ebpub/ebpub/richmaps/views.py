from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django import template
from django.template.loader import select_template
from django.utils.cache import patch_response_headers
from django.utils import simplejson
from ebpub.utils.view_utils import eb_render
from ebpub.db.models import NewsItem, Schema
from ebpub.openblockapi.views import _copy_nomulti, JSON_CONTENT_TYPE
from ebpub.openblockapi.itemquery import build_item_query
from ebpub.streets.models import Place, PlaceType
import datetime
import re

def bigmap(request):
    
    config = _decode_map_permalink(request)

    return eb_render(request, 'richmaps/bigmap.html', {
        'map_config': simplejson.dumps(config, indent=2)
    })

def _decode_map_permalink(request):
    """
    request parameters: 
    c - map center 
    z - map zoom 
    l - layer info
    p - popup center
    f - popup feature
    s - start date (inclusive) %m/%d/%Y
    e - end date (inclusive) %m/%d/%Y
    """
    
    params = request.GET
    
    #
    # enabled item, place layers "l" parameter
    #
    # l=p13,t32,p1 ...
    #
    # p => place layer
    # t => schema layer 
    # remaining portion is dbid of place or schema
    #
    schemas = set()
    place_types = set()
    lids = params.get("l", None)
    if lids is not None: 
        no_layers_specified = False
        try:
            pat = re.compile('(\w\d+)')
            for lid in pat.findall(lids):
                layer_type = lid[0]
                layer_id = int(lid[1:])
                if layer_type == 'p': 
                    place_types.add(layer_id)
                elif layer_type == 't': 
                    schemas.add(layer_id)
        except: 
            pass
    else: 
        no_layers_specified = True

    # map center
    center = params.get("c", None)
    if center: 
        try:
            center = [float(x) for x in center.split('_')][0:2]
        except: 
            pass
    
    # map zoom level 
    zoom = params.get("z", None)
    if zoom:
        try:
            zoom = float(zoom)
        except: 
            pass
        
    # popup 
    popup_info = None
    popup_center = params.get("p", None)
    popup_feature = params.get("f", None)
    if popup_center and popup_feature: 
        try:
            popup_center = [float(x) for x in popup_center.split('_')][0:2]
            feature_type = popup_feature[0]
            feature_id = int(popup_feature[1:])
            if feature_type == 'p': 
                openblock_type = 'place'
            elif feature_type == 't': 
                openblock_type = 'newsitem'

            popup_info = {
                'id': feature_id,
                'openblock_type': openblock_type,
                'lonlat': [popup_center[0], popup_center[1]]
            }
        except: 
            popup_center = None
            popup_feature = None
    

    # start and end date range
    startdate = params.get('s')
    if startdate is not None:
        try:
            startdate = datetime.datetime.date.strptime(startdate, '%m/%d/%Y').date()
        except:
            startdate = None

    enddate = params.get('e')
    if enddate is not None: 
        try:
            enddate = datetime.datetime.date.strptime(enddate, '%m/%d/%Y').date()
        except:
            enddate = None
    
    # fill in any missing or invalid dates
    max_interval = datetime.timedelta(days=7)
    if startdate is None and enddate is None:
        enddate = datetime.date.today()
        startdate = enddate - max_interval
    elif startdate is None: 
        startdate = enddate - max_interval
    elif enddate is None: 
        enddate = startdate + max_interval
    
    if enddate < startdate or enddate - startdate > max_interval:
        enddate = startdate + datetime.timedelta(days=7)

    layers = []
    for place_type in PlaceType.objects.filter(is_mappable=True).all():
        layers.append({
            'id': 'p%d' % place_type.id,
            'title': place_type.plural_name,
            'url': reverse('place_detail_json', args=[place_type.slug]),
            'params': {'limit': 1000},
            'minZoom': 15,
            'bbox': True,
            'visible': place_type.id in place_types # off by default
        })

    api_startdate = startdate.strftime("%Y-%m-%d")  
    api_enddate = (enddate + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    for schema in Schema.objects.filter(is_public=True).all():
        layers.append({
            'id': 't%d' % schema.id,
            'title':  schema.plural_name,
            'url':    reverse('map_items_json'),
            'params': {'type': schema.slug, 'limit': 1000,
                       'startdate': api_startdate,
                       'enddate': api_enddate},
            'bbox': False,
            'visible': no_layers_specified or schema.id in schemas # default on if no 't' param given
        })

    config = {
      'center': center or [settings.DEFAULT_MAP_CENTER_LON,
                           settings.DEFAULT_MAP_CENTER_LAT],
                           
      'zoom': zoom or settings.DEFAULT_MAP_ZOOM,
      
      'layers': layers, 
      
      'permalink_params': {
        's': startdate.strftime('%m/%d/%Y'),
        'e': enddate.strftime('%m/%d/%Y')
      }
    }
    
    if popup_info: 
        config['popup'] = popup_info
    
    return config


def item_popup(request, item_id):
    """
    Given a list of newsitems, return a list of lists
    of the form [newsitem_id, popup_html, schema_name]
    """
    try:
        item_id = int(item_id)
        ni = NewsItem.objects.get(id=item_id)
    except:
        return HttpResponse(status=404)

    schema = ni.schema
    template_list = ['richmaps/newsitem_popup_%s.html' % schema.slug,
                     'richmaps/newsitem_popup.html',
                     ]
    current_template = select_template(template_list)
    html = current_template.render(template.Context({'newsitem': ni, 'schema': schema, }))
    response = HttpResponse(html)
    patch_response_headers(response, cache_timeout=3600)
    return response

def place_popup(request, place_id):
    try: 
        place_id = int(place_id)
        place = Place.objects.get(id=place_id)
    except:
        return HttpResponse(status=404)

    template_list = ['richmaps/place_popup_%s.html' % place.place_type.slug,
                     'richmaps/place_popup.html',
                     ]
    current_template = select_template(template_list)
    html = current_template.render(template.Context({'place': place, 'place_type': place.place_type, }))
    response = HttpResponse(html)
    patch_response_headers(response, cache_timeout=3600)
    return response

def map_items_json(request):
    """
    slightly briefer and less attribute-accessing 
    rendition of the api's geojson response. includes
    only attributes used by the map.
    """
    items, params = build_item_query(_copy_nomulti(request.GET))
    
    def _item_to_feature(item):
        geom = simplejson.loads(item.location.geojson)
        result = {
            'type': 'Feature',
            'geometry': geom,
            }
        props = {'id': item.id,
                 'openblock_type': 'newsitem',
                 'icon': item.schema.map_icon_url,
                 'color': item.schema.map_color,
                }
        result['properties'] = props
        return result

    items = [_item_to_feature(item) for item in items if item.location is not None]
    items_geojson_dict = {'type': 'FeatureCollection',
                          'features': items
                          }
    
    body = simplejson.dumps(items_geojson_dict)
    response = HttpResponse(body, content_type=JSON_CONTENT_TYPE)
    patch_response_headers(response, cache_timeout=3600)
    return response
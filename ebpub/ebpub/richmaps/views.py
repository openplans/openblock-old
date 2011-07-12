from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django import template
from django.template.loader import select_template
from django.utils.cache import patch_response_headers
from django.utils import simplejson
from ebpub.utils.view_utils import eb_render
from ebpub.db.models import NewsItem, Schema
from ebpub.streets.models import Place, PlaceType
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
    
    
    layers = []
    for place_type in PlaceType.objects.filter(is_mappable=True).all():
        layers.append({
            'id': 'p%d' % place_type.id,
            'title': place_type.plural_name,
            'url': reverse('place_detail_json', args=[place_type.slug]),
            'params': {'limit': 150},
            'bbox': True,
            'visible': place_type.id in place_types # off by default
        })
    
    
    for schema in Schema.objects.filter(is_public=True).all():
        layers.append({
            'id': 't%d' % schema.id,
            'title':  schema.plural_name,
            'url':    reverse('items_json'),
            'params': {'type': schema.slug, 'limit': 150},
            'bbox': True,
            'visible': no_layers_specified or schema.id in schemas # default on if no 't' param given
        })

    config = {
      'center': center or [settings.DEFAULT_MAP_CENTER_LON,
                           settings.DEFAULT_MAP_CENTER_LAT],
                           
      'zoom': zoom or settings.DEFAULT_MAP_ZOOM,
      
      'layers': layers
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

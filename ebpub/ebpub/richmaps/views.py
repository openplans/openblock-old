from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django import template
from django.shortcuts import get_object_or_404
from django.template.loader import get_template, select_template
from django.utils.cache import patch_response_headers
from django.utils.datastructures import SortedDict
from django.utils import simplejson
from ebpub.utils.view_utils import eb_render
from ebpub.db.models import NewsItem, Schema, SchemaField
from ebpub.openblockapi.views import _copy_nomulti, JSON_CONTENT_TYPE
from ebpub.openblockapi.itemquery import build_item_query
from ebpub.db.schemafilters import FilterError
from ebpub.db.schemafilters import FilterChain
from ebpub.db.schemafilters import BadAddressException
from ebpub.db.schemafilters import BadDateException
from ebpub.streets.models import Place, PlaceType
from ebpub.utils.view_utils import get_schema_manager
import datetime
import re




def bigmap_filter(request, slug, args_from_url):
    
    s = get_object_or_404(get_schema_manager(request), slug=slug, is_special_report=False)
    if not s.allow_charting:
        return HttpResponse(status=404)

    filter_sf_list = list(SchemaField.objects.filter(schema__id=s.id, is_filter=True).order_by('display_order'))
    textsearch_sf_list = list(SchemaField.objects.filter(schema__id=s.id, is_searchable=True).order_by('display_order'))

    # Use SortedDict to preserve the display_order.
    filter_sf_dict = SortedDict([(sf.name, sf) for sf in filter_sf_list] + [(sf.name, sf) for sf in textsearch_sf_list])

    # Determine what filters to apply, based on path and/or query string.
    filterchain = FilterChain(request=request, schema=s)
    try:
        filterchain.update_from_request(args_from_url, filter_sf_dict)
        filters_need_more = filterchain.validate()
    except:
        return HttpResponse(status=404)
        
    config = _decode_map_permalink(request, show_default_layers=False, filters=filterchain)

    new_url = filterchain.make_url(base_url=reverse('bigmap_filter', args=(slug,)))
    if new_url != request.get_full_path():
        return HttpResponseRedirect(new_url)    

    
    # add in the filter layer
    base_url = reverse('ebpub-schema-filter-geojson', args=(slug,))
    layer_url = filterchain.make_url(base_url=base_url)
    custom_layer = {
        'url': layer_url,
        'params': {},
        'title': "Custom Filter",
        'visible': True
    }
    config['layers'].append(custom_layer)



    if config['is_widget']: 
        return eb_render(request, 'richmaps/embed_bigmap.html', {
            'map_config': simplejson.dumps(config, indent=2)
        })
    else:         
        return eb_render(request, 'richmaps/bigmap.html', {
            'map_config': simplejson.dumps(config, indent=2)
        })


def bigmap(request):
    config = _decode_map_permalink(request)

    if config['is_widget']: 
        return eb_render(request, 'richmaps/embed_bigmap.html', {
            'map_config': simplejson.dumps(config, indent=2)
        })
    else:         
        return eb_render(request, 'richmaps/bigmap.html', {
            'map_config': simplejson.dumps(config, indent=2)
        })

def _decode_map_permalink(request, show_default_layers=True, filters=None):
    """
    request parameters: 
    c - map center 
    z - map zoom 
    l - layer info
    p - popup center
    f - popup feature
    start_date - start date (inclusive) %m/%d/%Y
    end_date - end date (inclusive) %m/%d/%Y
    d - duration in days (overridden by end date)

    x - show as 'widget' 
    v- limits what map controls are displayed (widget only)
    w - width of map (widget only)
    h - height of map (widget only)
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
    startdate = params.get('start_date')
    if startdate is not None:
        try:
            startdate = datetime.datetime.strptime(startdate, '%m/%d/%Y').date()
        except:
            startdate = None

    enddate = params.get('end_date')
    if enddate is not None: 
        try:
            enddate = datetime.datetime.strptime(enddate, '%m/%d/%Y').date()
        except:
            enddate = None

    if startdate is None and enddate is None and filters:
        date_filter = filters.get('date') or filters.get('pubdate')
        if date_filter:
            startdate = date_filter.start_date
            enddate = date_filter.end_date


    default_interval = datetime.timedelta(days=7)
    duration = params.get('d')
    if duration is not None:
        try:
            duration = datetime.timedelta(days=int(duration))
        except:
            duration = default_interval
    else: 
        duration = default_interval

    if startdate is None and enddate is None:
        enddate = datetime.date.today()
        startdate = enddate - duration
    elif startdate is None:
        startdate = enddate - duration
    elif enddate is None:
        enddate = startdate + duration

    if enddate < startdate:
        enddate = startdate + duration

    # inject date range into filters if none was specified:
    if filters and filters.get('date') is None: 
        filters.add('date', startdate, enddate)

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
            'visible': (no_layers_specified and show_default_layers) or schema.id in schemas # default on if no 't' param given
        })

    is_widget = params.get('x', None) is not None
        
    controls = {}
    control_list = params.get("v", None)
    if control_list is not None: 
        if 'l' in control_list: 
            controls['layers'] = True
        if 'h' in control_list: 
            controls['headline_list'] = True
        if 'p' in control_list: 
            controls['permalink'] = True

    width = params.get("w", None)
    if width:
        try:
            width = int(width)
        except: 
            width = None

    height = params.get("h", None)
    if height:
        try:
            height = int(height)
        except: 
            height = None

    config = {
      'center': center or [settings.DEFAULT_MAP_CENTER_LON,
                           settings.DEFAULT_MAP_CENTER_LAT],

      'zoom': zoom or settings.DEFAULT_MAP_ZOOM,
      
      'layers': layers, 
      
      'is_widget': is_widget,
      
      'permalink_params': {
        'start_date': startdate.strftime('%m/%d/%Y'),
        'end_date': enddate.strftime('%m/%d/%Y'),
      }, 
    }


    if popup_info:
        config['popup'] = popup_info

    
    if is_widget: 
        config['controls'] = controls
        if width is not None: 
            config['width'] = width
        if height is not None: 
            config['height'] = height
    
    return config

def headlines(request):
    html = ''
    items = request.REQUEST.getlist('item_id')
    items = [x.split(':') for x in items]
    if len(items) == 0:
        cur_template = get_template('richmaps/no_headlines.html')
        html = cur_template.render(template.Context({}))
    else: 
        for (obtype, item_id) in items:
            if obtype == 'newsitem':
                html += _item_headline(request, item_id)
            else: 
                html += _place_headline(request, item_id)

    response = HttpResponse(html)
    patch_response_headers(response, cache_timeout=3600)
    return response


def _item_headline(request, item_id):
    """
    returns the headline list html for a single item.
    """
    try:
        item_id = int(item_id)
        ni = NewsItem.objects.get(id=item_id)
    except:
        return ''

    schema = ni.schema
    template_list = ['richmaps/newsitem_headline_%s.html' % schema.slug,
                     'richmaps/newsitem_headline.html',
                     ]
    current_template = select_template(template_list)
    return current_template.render(template.Context({'newsitem': ni, 'schema': schema, }))


def _place_headline(request, item_id):
    """
    returns the headline list html for a single place.
    """
    try:
        item_id = int(item_id)
        place = Place.objects.get(id=item_id)
        place_type = place.place_type
    except:
        return ''


    template_list = ['richmaps/place_headline_%s.html' % place_type.slug,
                     'richmaps/place_headline.html',
                     ]
    current_template = select_template(template_list)
    return current_template.render(template.Context({'place': place, 'place_type': place_type, }))


def item_popup(request, item_id):
    """
    returns the popup html for a single item.
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
    
        sort_key = '%d-%d-%d-%s-%d' % (9999 - item.item_date.year,
                                    13 - item.item_date.month,
                                    32 - item.item_date.day,
                                    item.title,
                                    item.id)
        props = {'id': item.id,
                 'openblock_type': 'newsitem',
                 'icon': item.schema.map_icon_url,
                 'color': item.schema.map_color,
                 'sort': sort_key
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

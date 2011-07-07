from django.conf import settings
from django.http import HttpResponse
from django import template
from django.template.loader import select_template
from django.utils.cache import patch_response_headers
from ebpub.utils.view_utils import eb_render
from ebpub.db.models import NewsItem
from ebpub.streets.models import Place

def bigmap(request):
    return eb_render(request, 'richmaps/bigmap.html', {
        'default_lon': settings.DEFAULT_MAP_CENTER_LON,
        'default_lat': settings.DEFAULT_MAP_CENTER_LAT,
        'default_zoom': settings.DEFAULT_MAP_ZOOM,
#        'bodyclass': 'homepage',
#        'breadcrumbs': breadcrumbs.home({}),
    })


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

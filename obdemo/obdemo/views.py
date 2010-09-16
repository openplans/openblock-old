"""
Views for openblock demo.

If these turn out to be really useful they could be merged upstream
into ebpub.
"""

from django.contrib.gis.shortcuts import render_to_kml
from django.http import HttpResponse
from django.utils import simplejson
from ebpub.db.models import Location
from ebpub.db.models import NewsItem
from ebpub.db.views import make_search_buffer
from ebpub.db.views import map_popups
from ebpub.db.views import parse_pid
from ebpub.streets.models import Block

def newsitems_geojson(request):
    # Copy-pasted code from ajax_place_newsitems.  Refactoring target:
    # Seems like there are a number of similar code blocks in
    # ebpub.db.views?

    pid = request.GET.get('pid', '')

    if pid:
        place, block_radius, xy_radius = parse_pid(pid)
        if isinstance(place, Block):
            search_buffer = make_search_buffer(place.location.centroid, block_radius)
            newsitem_qs = NewsItem.objects.filter(location__bboverlaps=search_buffer)
        else:
            # This depends on the trigger in newsitemlocation.sql
            newsitem_qs = NewsItem.objects.filter(
                newsitemlocation__location__id=place.id)
    else:
        # Whole city!
        newsitem_qs = NewsItem.objects.all()

    # Ordering by schema__id is an optimization for map_popups()
    newsitem_list = list(newsitem_qs.select_related().order_by('schema__id'))
    popup_list = map_popups(newsitem_list)

    features = {'type': 'FeatureCollection', 'features': []}
    for newsitem, popup_info in zip(newsitem_list, popup_list):
        if newsitem.location is None:
            # Can happen, see NewsItem docstring.
            # TODO: We should probably allow for newsitems that have a
            # location_object too?
            continue

        features['features'].append(
            {'type': 'Feature',
             'geometry': {'type': 'Point',
                          'coordinates': [newsitem.location.centroid.x,
                                          newsitem.location.centroid.y],
                          },
             'properties': {
                    'title': newsitem.title,
                    'id': popup_info[0],
                    'popup_html': popup_info[1],
                    'schema': popup_info[2],
                    }
             })
    output = simplejson.dumps(features, indent=2)
    return HttpResponse(output, mimetype="application/javascript")


from ebpub.db.views import url_to_place

def place_kml(request, *args, **kwargs):
    place = url_to_place(*args, **kwargs)
    return render_to_kml('place.kml', {'place': place})

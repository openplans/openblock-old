"""
Views for openblock demo.

If these turn out to be really useful they could be merged upstream
into ebpub.
"""

from django.http import HttpResponse
from django.utils import simplejson
from django.db.models import Q

from ebpub.db.views import parse_pid
from ebpub.db.views import make_search_buffer
from ebpub.streets.models import Block
from ebpub.db.models import NewsItem

def newsitems_geojson(request):
    # Copy-pasted code from ajax_place_newsitems.  Refactoring target:
    # Seems like there are a number of similar code blocks in
    # ebpub.db.views?

    #pid = request.GET.get('pid', '')
    pid = 'l:7'  # East Boston got a bunch from my random script.
    place, block_radius, xy_radius = parse_pid(pid)

    if isinstance(place, Block):
        search_buffer = make_search_buffer(place.location.centroid, block_radius)
        newsitem_qs = NewsItem.objects.filter(location__bboverlaps=search_buffer)
    else:
        # This depends on the trigger in newsitemlocation.sql
        newsitem_qs = NewsItem.objects.filter(
            newsitemlocation__location__id=place.id)


    features = {'type': 'FeatureCollection', 'features': []}
    for newsitem in newsitem_qs:
        features['features'].append(
            {'type': 'Feature',
             'geometry': {'type': 'Point',
                          'coordinates': [newsitem.location.centroid.x,
                                          newsitem.location.centroid.y],
                          },
             'properties': {
                    'title': newsitem.title,
                    }
             })
    output = simplejson.dumps(features, indent=2)
    return HttpResponse(output, mimetype="application/javascript")

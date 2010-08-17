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
        # I'm puzzled about when/how NewsItemLocations get created,
        # they're clearly just a simple join table but
        # I can't find anything that would populate when news items
        # are created,
        # except maybe a trigger function in ebpub/ebpub/db/sql/newsitemlocation_functions.sql
        # which AFAICT is not referred to by anything, so I'm not sure if I'm
        # supposed to have installed that function or what.
        # 
        # I *do* see code in ebpub/db/bin/*py to populate that table
        # from existing newsitems when locations are added, but not
        # when newsitems are added AFAICT.
        #
        # So I'm hacking around it by ORing the query together with a
        # test for news items that are directly associated with that
        # Location. Why existing ebpub code doesn't do that, I do not
        # know.
        # newsitem_qs = NewsItem.objects.filter(
        #     Q(newsitemlocation__location__id=place.id) |
        #     Q(location_object__id=place.id))

        # ... scratch all that, the trigger in 
        # newsitemlocation_functions.sql appears to be what we want.
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

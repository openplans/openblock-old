"""
Views for openblock demo.

If these turn out to be really useful they could be merged upstream
into ebpub.
"""
from django.contrib.gis.shortcuts import render_to_kml
from django.http import HttpResponse
from django.core.cache import cache
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.utils.cache import patch_response_headers
from django.views.decorators.cache import cache_page
from ebpub.db import constants
from ebpub.db import views
from ebpub.db.models import NewsItem
from ebpub.db.utils import today
from ebpub.streets.models import Block
from ebpub.utils.view_utils import parse_pid
import datetime
import hashlib


def newsitems_geojson(request):
    """Get a list of newsitems, optionally filtered for one place ID
    and/or one schema slug.

    Response is a geojson string.
    """
    # Note: can't use @cache_page here because that ignores all requests
    # with query parameters (in FetchFromCacheMiddleware.process_request).
    # So, we'll use the low-level cache API.

    # Copy-pasted code from ajax_place_newsitems.  Refactoring target:
    # Seems like there are a number of similar code blocks in
    # ebpub.db.views?

    pid = request.GET.get('pid', '')
    schema = request.GET.get('schema', '')

    cache_seconds = 60 * 5
    cache_key = 'newsitem_geojson_%s_%s' % (pid, schema)

    newsitem_qs = NewsItem.objects.all()
    if schema:
        newsitem_qs = newsitem_qs.filter(schema__slug=schema)
    if pid:
        place, block_radius, xy_radius = parse_pid(pid)
        if isinstance(place, Block):
            search_buffer = views.make_search_buffer(place.location.centroid, block_radius)
            newsitem_qs = newsitem_qs.filter(location__bboverlaps=search_buffer)
        else:
            # This depends on the trigger in newsitemlocation.sql
            newsitem_qs = newsitem_qs.filter(
                newsitemlocation__location__id=place.id)
    else:
        # Whole city!
        pass

    # More copy/paste from ebpub.db.views...
    # As an optimization, limit the NewsItems to those published in the
    # last few days.
    end_date = today()
    start_date = end_date - datetime.timedelta(days=constants.LOCATION_DAY_OPTIMIZATION)
    newsitem_qs = newsitem_qs.filter(pub_date__gt=start_date-datetime.timedelta(days=1), pub_date__lt=end_date+datetime.timedelta(days=1)).select_related()
    if not views.has_staff_cookie(request):
        newsitem_qs = newsitem_qs.filter(schema__is_public=True)

    # Ordering by schema__id is an optimization for map_popups()
    newsitem_qs = newsitem_qs.select_related().order_by('schema__id')
    # And, put a hard limit on the number of newsitems.
    newsitem_qs = newsitem_qs[:constants.NUM_NEWS_ITEMS_PLACE_DETAIL]

    # Done preparing the query; cache based on the raw SQL
    # to be sure we capture everything that matters.
    cache_key += hashlib.md5(str(newsitem_qs.query)).hexdigest()
    output = cache.get(cache_key, None)
    if output is None:
        newsitem_list = list(newsitem_qs)
        popup_list = views.map_popups(newsitem_list)

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
        output = simplejson.dumps(features, indent=1)
        cache.set(cache_key, output, cache_seconds)

    response = HttpResponse(output, mimetype="application/javascript")
    patch_response_headers(response, cache_timeout=60 * 5)
    return response


@cache_page(60 * 60)
def place_kml(request, *args, **kwargs):
    place = views.url_to_place(*args, **kwargs)
    return render_to_kml('place.kml', {'place': place})

def geotagger_ui(request): 
    return render_to_response('geotagger/geotagger.html', RequestContext(request, {}))

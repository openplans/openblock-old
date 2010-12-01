"""
Views for openblock demo.

If these turn out to be really useful they could be merged upstream
into ebpub.
"""
from django.conf import settings
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
from ebpub.db.models import AggregateDay
from ebpub.db.models import NewsItem
from ebpub.db.models import Schema
from ebpub.db.models import LocationType
from ebpub.db.utils import today
from ebpub.db.views import get_date_chart_agg_model
from ebpub.streets.models import Block
from ebpub.streets.models import Street
from ebpub.utils.view_utils import eb_render
from ebpub.utils.view_utils import parse_pid

import datetime
import hashlib


def homepage(request):
    """A slimmed-down version of ebpub.db.views.homepage.
    """

    end_date = today()
    start_date = end_date - datetime.timedelta(days=settings.DEFAULT_DAYS)
    end_date += datetime.timedelta(days=1)

    sparkline_schemas = list(Schema.public_objects.filter(allow_charting=True, is_special_report=False))

    # Order by slug to ensure case-insensitive ordering. (Kind of hackish.)
    lt_list = LocationType.objects.filter(is_significant=True).order_by('slug').extra(select={'count': 'select count(*) from db_location where is_public=True and location_type_id=db_locationtype.id'})
    street_count = Street.objects.count()
    more_schemas = Schema.public_objects.filter(allow_charting=False).order_by('name')

    # Get the public records.
    date_charts = get_date_chart_agg_model(sparkline_schemas, start_date, end_date, AggregateDay)
    empty_date_charts, non_empty_date_charts = [], []
    for chart in date_charts:
        if chart['total_count']:
            non_empty_date_charts.append(chart)
        else:
            empty_date_charts.append(chart)
    non_empty_date_charts.sort(lambda a, b: cmp(b['total_count'], a['total_count']))
    empty_date_charts.sort(lambda a, b: cmp(a['schema'].plural_name, b['schema'].plural_name))

    return eb_render(request, 'homepage.html', {
        'location_type_list': lt_list,
        'street_count': street_count,
        'more_schemas': more_schemas,
        'non_empty_date_charts': non_empty_date_charts,
        'empty_date_charts': empty_date_charts,
        'num_days': settings.DEFAULT_DAYS,
        'default_lon': settings.DEFAULT_MAP_CENTER_LON,
        'default_lat': settings.DEFAULT_MAP_CENTER_LAT,
        'default_zoom': settings.DEFAULT_MAP_ZOOM,
    })

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
    start_date = end_date - datetime.timedelta(days=settings.DEFAULT_DAYS)
    # Bug http://developer.openblockproject.org/ticket/77:
    # This is using pub_date, but Aggregates use item_date, so there's
    # a visible disjoint between number of items on the map and the item
    # count shown on the homepage and location detail page.
    newsitem_qs = newsitem_qs.filter(pub_date__gt=start_date-datetime.timedelta(days=1), pub_date__lt=end_date+datetime.timedelta(days=1)).select_related()
    if not views.has_staff_cookie(request):
        newsitem_qs = newsitem_qs.filter(schema__is_public=True)

    # Put a hard limit on the number of newsitems, and throw away older items.
    newsitem_qs = newsitem_qs.select_related().order_by('-pub_date')
    newsitem_qs = newsitem_qs[:constants.NUM_NEWS_ITEMS_PLACE_DETAIL]

    # Done preparing the query; cache based on the raw SQL
    # to be sure we capture everything that matters.
    cache_key += hashlib.md5(str(newsitem_qs.query)).hexdigest()
    output = cache.get(cache_key, None)
    if output is None:
        # Re-sort by schema type.
        # This is an optimization for map_popups().
        # We can't do it in the qs because we want to first slice the qs
        # by date, and we can't call order_by() after a slice.
        newsitem_list = sorted(newsitem_qs, key=lambda ni: ni.schema.id)
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

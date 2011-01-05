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


def geotagger_ui(request): 
    return render_to_response('geotagger/geotagger.html', RequestContext(request, {}))

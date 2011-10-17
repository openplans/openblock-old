#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.contrib.gis.shortcuts import render_to_kml
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson
from django.utils.cache import patch_response_headers
from django.utils.datastructures import SortedDict
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from ebpub.constants import HIDE_ADS_COOKIE_NAME, HIDE_SCHEMA_INTRO_COOKIE_NAME
from ebpub.db import breadcrumbs
from ebpub.db import constants
from ebpub.db.models import AggregateDay, AggregateLocation, AggregateFieldLookup
from ebpub.db.models import NewsItem, Schema, SchemaField, LocationType, Location, SearchSpecialCase
from ebpub.db.schemafilters import FilterError
from ebpub.db.schemafilters import FilterChain
from ebpub.db.schemafilters import BadAddressException
from ebpub.db.schemafilters import BadDateException

from ebpub.db.utils import populate_attributes_if_needed, populate_schema, today
from ebpub.db.utils import url_to_place
from ebpub.db.utils import get_place_info_for_request
from ebpub import geocoder
from ebpub.geocoder.parser.parsing import normalize
from ebpub.metros.allmetros import get_metro
from ebpub.openblockapi.views import api_items_geojson
from ebpub.preferences.models import HiddenSchema
from ebpub.streets.models import Street, City, Block, Intersection
from ebpub.streets.utils import full_geocode
from ebpub.utils.dates import daterange, parse_date
from ebpub.utils.view_utils import eb_render
from ebpub.utils.view_utils import get_schema_manager
from ebpub.utils.view_utils import has_staff_cookie

import datetime
import hashlib
import logging
import operator
import re

logger = logging.getLogger('ebpub.db.views')

################################
# HELPER FUNCTIONS (NOT VIEWS) #
################################


def get_date_chart_agg_model(schemas, start_date, end_date, agg_model, kwargs=None):
    """start_date and end_date are *inclusive*.
    """
    kwargs = kwargs or {}
    counts = {}
    for agg in agg_model.objects.filter(schema__id__in=[s.id for s in schemas], date_part__range=(start_date, end_date), **kwargs):
        counts.setdefault(agg.schema_id, {})[agg.date_part] = agg.total
    return get_date_chart(schemas, start_date, end_date, counts)

def get_date_chart(schemas, start_date, end_date, counts):
    """
    Returns a list that's used to display a date chart for the given
    schemas. Note that start_date and end_date should be datetime.date objects,
    NOT datetime.datetime objects, and they are *inclusive*,
    i.e. the resulting chart will include both start_date and end_date.

    counts should be a nested dictionary: {schema_id: {date: count}}

    The list will be in order given by the `schemas` parameter.
    """
    result = []
    for schema in schemas:
        if schema.id not in counts:
            result.append({
                'schema': schema,
                'dates': [{'date': d, 'count': 0} for d in daterange(start_date, end_date)],
                'max_count': 0,
                'total_count': 0,
                'latest_date': None,
            })
        else:
            dates = [{'date': d, 'count': counts[schema.id].get(d, 0)} for d in daterange(start_date, end_date)]
            nonzero_dates = [d['date'] for d in dates if d['count']]
            if nonzero_dates:
                latest_date = max(nonzero_dates)
            else:
                latest_date = None
            result.append({
                'schema': schema,
                'dates': dates,
                'max_count': max(d['count'] for d in dates),
                'total_count': sum(d['count'] for d in dates),
                'latest_date': latest_date,
            })
    return result


def block_bbox(block, radius):
    """
    Assumes `block' has `wkt' attribute
    """
    try:
        from osgeo import ogr
    except ImportError:
        import ogr
    env = ogr.CreateGeometryFromWkt(block.wkt).Buffer(radius).GetEnvelope()
    return (env[0], env[2], env[1], env[3])




##############
# AJAX VIEWS #
##############


def ajax_place_lookup_chart(request):
    """
    Returns HTML fragment -- expects request.GET['pid'] and request.GET['sf'] (a SchemaField ID).
    """
    try:
        sf = SchemaField.objects.select_related().get(id=int(request.GET['sf']), schema__is_public=True)
    except (KeyError, ValueError, SchemaField.DoesNotExist):
        raise Http404('Invalid SchemaField')
    filters = FilterChain(request=request, schema=sf.schema)
    filters.add_by_place_id(request.GET.get('pid', ''))
    qs = filters.apply()
    total_count = qs.count()
    top_values = qs.top_lookups(sf, 10)
    return render_to_response('db/snippets/lookup_chart.html', {
        'lookup': {'sf': sf, 'top_values': top_values},
        'total_count': total_count,
        'schema': sf.schema,
        'filters': filters,
    })

def ajax_place_date_chart(request):
    """
    Returns HTML fragment containing a chart of how many news items
    were added for each day over a short period (length defined by
    constants.DAYS_SHORT_AGGREGATE_TIMEDELTA).

    Expects request.GET['pid'] and request.GET['s'] (a Schema ID).
    """
    try:
        schema = Schema.public_objects.get(id=int(request.GET['s']))
    except (KeyError, ValueError, Schema.DoesNotExist):
        raise Http404('Invalid Schema')
    filters = FilterChain(request=request, schema=schema)
    filters.add_by_place_id(request.GET.get('pid', ''))
    qs = filters.apply()

    # These charts are used on eg. the place overview page; there,
    # they should be smaller than the ones on the schema_detail view;
    # we don't have room for a full 30 days.
    date_span = constants.DAYS_SHORT_AGGREGATE_TIMEDELTA
    if schema.is_event:
        # Soonest span that includes some.
        try:
            qs = qs.filter(item_date__gte=today()).order_by('item_date', 'id')
            first_item = qs.values('item_date')[0]
            start_date = first_item['item_date']
        except IndexError:  # No matching items.
            start_date = today()
        end_date = today() + date_span
    else:
        # Most recent span that includes some.
        try:
            qs = qs.filter(item_date__lte=today()).order_by('-item_date', '-id')
            last_item = qs.values('item_date')[0]
            end_date = last_item['item_date']
        except IndexError:  # No matching items.
            end_date = today()
        start_date = end_date - date_span

    filters.add('date', start_date, end_date)
    counts = filters.apply().date_counts()
    date_chart = get_date_chart([schema], start_date, end_date, {schema.id: counts})[0]
    return render_to_response('db/snippets/date_chart.html', {
        'schema': schema,
        'date_chart': date_chart,
        'filters': filters,
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
    schema = request.GET.get('schema', None)
    if schema is not None:
        schema = get_object_or_404(Schema, slug=schema)

    nid = request.GET.get('newsitem', '')

    newsitem_qs = NewsItem.objects.all()
    if nid:
        newsitem_qs = newsitem_qs.filter(id=nid)
    else:
        filters = FilterChain(request=request, queryset=newsitem_qs, schema=schema)
        if pid:
            filters.add_by_place_id(pid)
        else:
            # Whole city!
            pass

        # More copy/paste from ebpub.db.views...
        # As an optimization, limit the NewsItems to those published in the
        # last few days.
        filters.update_from_query_params(request)
        if not filters.has_key('date'):
            end_date = today()
            start_date = end_date - datetime.timedelta(days=settings.DEFAULT_DAYS)
            filters.add('date', start_date, end_date)
        newsitem_qs = filters.apply()
        newsitem_qs = newsitem_qs
        if not has_staff_cookie(request):
            newsitem_qs = newsitem_qs.filter(schema__is_public=True)

        # Put a hard limit on the number of newsitems, and throw away
        # older items.
        newsitem_qs = newsitem_qs.select_related().order_by('-item_date', '-id')
        newsitem_qs = newsitem_qs[:constants.NUM_NEWS_ITEMS_PLACE_DETAIL]

    # Done preparing the query; cache based on the raw SQL
    # to be sure we capture everything that matters.
    cache_seconds = 60 * 5
    cache_key = 'newsitem_geojson:' + _make_cache_key_from_queryset(newsitem_qs)
    output = cache.get(cache_key, None)
    if output is None:
        newsitem_list = list(newsitem_qs)
        output = api_items_geojson(newsitem_list)
        cache.set(cache_key, output, cache_seconds)

    response = HttpResponse(output, mimetype="application/javascript")
    patch_response_headers(response, cache_timeout=60 * 5)
    return response

def _make_cache_key_from_queryset(qs):
    cache_key = 'query:'
    cache_key += hashlib.md5(str(qs.query)).hexdigest()
    return cache_key

@cache_page(60 * 60)
def place_kml(request, *args, **kwargs):
    place = url_to_place(*args, **kwargs)
    return render_to_kml('place.kml', {'place': place})


#########
# VIEWS #
#########


def homepage(request):
    """Front page of the default OpenBlock theme.
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
        'bodyclass': 'homepage',
        'breadcrumbs': breadcrumbs.home({}),
        'map_configuration': _preconfigured_map({})
    })

def search(request, schema_slug=''):
    "Performs a location search and redirects to the address/xy page."
    # Check whether a schema was provided.
    if schema_slug:
        try:
            schema = get_schema_manager(request).get(slug=schema_slug)
        except Schema.DoesNotExist:
            raise Http404('Schema does not exist')
        url_prefix = schema.url()[:-1]
    else:
        schema = None
        url_prefix = ''

    # Get the query.
    q = request.GET.get('q', '').strip()
    if not q:
        return HttpResponseRedirect(url_prefix + '/') # TODO: Do something better than redirecting.

    # For /search/?type=alert, we redirect results to the alert page, not the
    # place page.
    if request.GET.get('type', '') == 'alert':
        url_method = 'alert_url'
    else:
        url_method = 'url'

    # Try to geocode it using full_geocode().
    try:
        result = full_geocode(q, search_places=False)
    except: # TODO: Naked except clause.
        pass
    else:
        if result['ambiguous']:
            if result['type'] == 'block':
                return eb_render(request, 'db/search_invalid_block.html', {
                    'query': q,
                    'choices': result['result'],
                    'street_name': result['street_name'],
                    'block_number': result['block_number']
                })
            else:
                return eb_render(request, 'db/did_you_mean.html', {'query': q, 'choices': result['result']})
        elif result['type'] == 'location':
            return HttpResponseRedirect(url_prefix + getattr(result['result'], url_method)())
        elif result['type'] == 'address':
            # Block
            if result['result']['block']:
                return HttpResponseRedirect(url_prefix + getattr(result['result']['block'], url_method)())
            # Intersection
            try:
                intersection = Intersection.objects.get(id=result['result']['intersection_id'])
            except Intersection.DoesNotExist:
                pass
            else:
                return HttpResponseRedirect(url_prefix + getattr(intersection, url_method)())

    # Failing the geocoding, look in the special-case table.
    try:
        special_case = SearchSpecialCase.objects.get(query=normalize(q))
    except SearchSpecialCase.DoesNotExist:
        pass
    else:
        if special_case.redirect_to:
            return HttpResponseRedirect(special_case.redirect_to)
        else:
            return eb_render(request, 'db/search_special_case.html', {'query': q, 'special_case': special_case})

    # Failing that, display a list of ZIP codes if this looks like a ZIP.
    if re.search(r'^\s*\d{5}(?:-\d{4})?\s*$', q):
        z_list = Location.objects.filter(location_type__slug='zipcodes', is_public=True).select_related().order_by('name')
        if z_list:
            return eb_render(request, 'db/search_error_zip_list.html', {'query': q, 'zipcode_list': z_list})

    # Failing all of that, display the search error page.
    lt_list = LocationType.objects.filter(is_significant=True).order_by('name')
    return eb_render(request, 'db/search_error.html', {'query': q, 'locationtype_list': lt_list})

@csrf_protect
def newsitem_detail(request, schema_slug, newsitem_id):
    ni = get_object_or_404(NewsItem.objects.select_related(), id=newsitem_id,
                           schema__slug=schema_slug)
    if not ni.schema.is_public and not has_staff_cookie(request):
        raise Http404('Not public')

    if not ni.schema.has_newsitem_detail:
        # Don't show detail pages.
        if ni.url:
            return HttpResponsePermanentRedirect(ni.url)
        else:
            # We have nothing to show the user; ticket #110.
            raise Http404("This news item needs an external URL and doesn't have one")

    atts = ni.attributes_for_template()

    has_location = ni.location is not None

    if has_location:
        locations_within = Location.objects.select_related().filter(
            newsitemlocation__news_item__id=ni.id)
        center_x = ni.location.centroid.x
        center_y = ni.location.centroid.y
    else:
        locations_within = ()
        center_x = settings.DEFAULT_MAP_CENTER_LON
        center_y = settings.DEFAULT_MAP_CENTER_LAT

    hide_ads = (request.COOKIES.get(HIDE_ADS_COOKIE_NAME) == 't')

    templates_to_try = ('db/newsitem_detail/%s.html' % ni.schema.slug, 'db/newsitem_detail.html')

    # Try to find a usable URL to link to from the location name.
    # TODO: move this logic to NewsItem.location_url()
    location_url = ni.location_url()
    if not location_url:
        # There might be any number of intersecting locations_within,
        # and we don't have any criteria for deciding which if any
        # best corresponds to ni.location_name; but we can try
        # a few other fallbacks.
        if ni.block:
            location_url = ni.block.url()
        elif ni.location:
            # Try reverse-geocoding and see if we get a block.
            try:
                block, distance = geocoder.reverse.reverse_geocode(ni.location)
                # TODO: if this happens, we should really update
                # ni.block, but this seems like a terrible place to do
                # that.
                logger.warn(
                    "%r (id %d) can be reverse-geocoded to %r (id %d) but"
                    " self.block isn't set" % (ni, ni.id, block, block.id))
                location_url = block.url()
            except geocoder.reverse.ReverseGeocodeError:
                logger.error(
                    "%r (id %d) has neither a location_url, nor a block,"
                    " nor a reverse-geocodable location" % (ni, ni.id))
                pass

    context = {
        'newsitem': ni,
        'attribute_list': [att for att in atts if att.sf.display],
        'attribute_dict': dict((att.sf.name, att) for att in atts),
        'has_location': has_location,
        'locations_within': locations_within,
        'location_url': location_url,
        'hide_ads': hide_ads,
        'map_center_x': center_x,
        'map_center_y': center_y,
        'bodyclass': 'newsitem-detail',
        'bodyid': schema_slug,
    }
    context['breadcrumbs'] = breadcrumbs.newsitem_detail(context)
    context['map_configuration'] = _preconfigured_map(context)
    return eb_render(request, templates_to_try, context)

def schema_list(request):
    schema_list = Schema.objects.select_related().filter(is_public=True, is_special_report=False).order_by('plural_name')
    schemafield_list = list(SchemaField.objects.filter(is_filter=True).order_by('display_order'))
    browsable_locationtype_list = LocationType.objects.filter(is_significant=True)
    # Populate s_list, which contains a schema and schemafield list for each schema.
    s_list = []
    for s in schema_list:
        s_list.append({
            'schema': s,
            'schemafield_list': [sf for sf in schemafield_list if sf.schema_id == s.id],
        })

    return eb_render(request, 'db/schema_list.html', {
        'schema_list': s_list,
        'browsable_locationtype_list': browsable_locationtype_list,
        'bodyclass': 'schema-list',
    })

def schema_detail(request, slug):
    s = get_object_or_404(get_schema_manager(request), slug=slug)
    if s.is_special_report:
        return schema_detail_special_report(request, s)

    location_type_list = LocationType.objects.filter(is_significant=True).order_by('slug')
    if s.allow_charting:
        # For the date range, the end_date is the last non-future date
        # with at least one NewsItem.
        try:
            end_date = NewsItem.objects.filter(schema__id=s.id, item_date__lte=today()).values_list('item_date', flat=True).order_by('-item_date')[0]
        except IndexError:
            latest_dates = ()
            date_chart = {}
            start_date = end_date = None
        else:
            start_date = end_date - constants.DAYS_AGGREGATE_TIMEDELTA
            date_chart = get_date_chart_agg_model([s], start_date, end_date, AggregateDay)[0]
            latest_dates = [date['date'] for date in date_chart['dates'] if date['count']]

        # Populate schemafield_list and lookup_list.
        schemafield_list = list(s.schemafield_set.filter(is_filter=True).order_by('display_order'))
        # XXX this duplicates part of schema_filter()
        LOOKUP_MIN_DISPLAYED = 7
        LOOKUP_BUFFER = 4
        lookup_list = []
        for sf in schemafield_list:
            if not (sf.is_charted and sf.is_lookup):
                continue
            top_values = list(AggregateFieldLookup.objects.filter(schema_field__id=sf.id).select_related('lookup').order_by('-total')[:LOOKUP_MIN_DISPLAYED + LOOKUP_BUFFER])
            if len(top_values) == LOOKUP_MIN_DISPLAYED + LOOKUP_BUFFER:
                top_values = top_values[:LOOKUP_MIN_DISPLAYED]
                has_more = True
            else:
                has_more = False
            lookup_list.append({'sf': sf, 'top_values': top_values, 'has_more': has_more})

        location_chartfield_list = []

        # Populate location_chartfield_list.
        for lt in location_type_list:
            # Collect the locations in the location_type here so we don't have
            # to query them again in the select_related() below.
            locations = dict([(loc.id, loc) for loc in lt.location_set.iterator()])

            ni_totals = AggregateLocation.objects.filter(
                schema__id=s.id,
                location_type__id=lt.id,
                location__is_public=True).select_related('location').order_by('-total')

            if ni_totals:  # This runs the query.
                known_count = reduce(operator.add, (n.total for n in ni_totals))
                total_count = date_chart.get('total_count', 0)
                unknown_count = max(0, total_count - known_count)
                location_chartfield_list.append({'location_type': lt, 'locations': ni_totals[:9], 'unknown': unknown_count})
        ni_list = ()
    else:
        date_chart = {}
        latest_dates = schemafield_list = lookup_list = location_chartfield_list = ()
        ni_list = list(NewsItem.objects.filter(schema__id=s.id).order_by('-item_date', '-id')[:30])
        populate_schema(ni_list, s)
        populate_attributes_if_needed(ni_list, [s])

    textsearch_sf_list = list(SchemaField.objects.filter(schema__id=s.id, is_searchable=True).order_by('display_order'))
    boolean_lookup_list = [sf for sf in SchemaField.objects.filter(schema__id=s.id, is_filter=True, is_lookup=False).order_by('display_order') if sf.is_type('bool')]

    templates_to_try = ('db/schema_detail/%s.html' % s.slug, 'db/schema_detail.html')

    # The HIDE_SCHEMA_INTRO_COOKIE_NAME cookie is a comma-separated list of
    # schema IDs for schemas whose intro text should *not* be displayed.
    hide_intro = str(s.id) in request.COOKIES.get(HIDE_SCHEMA_INTRO_COOKIE_NAME, '').split(',')

    context = {
        'schema': s,
        'schemafield_list': schemafield_list,
        'location_type_list': location_type_list,
        'date_chart': date_chart,
        'lookup_list': lookup_list,
        'location_chartfield_list': location_chartfield_list,
        'boolean_lookup_list': boolean_lookup_list,
        'search_list': textsearch_sf_list,
        'newsitem_list': ni_list,
        'latest_dates': latest_dates[-3:],
        'hide_intro': hide_intro,
        'hide_intro_cookie_name': HIDE_SCHEMA_INTRO_COOKIE_NAME,
        'start_date': s.min_date,
        'end_date': today(),
        'bodyclass': 'schema-detail',
        'bodyid': slug,
        'filters': FilterChain(schema=s),
    }
    context['breadcrumbs'] = breadcrumbs.schema_detail(context)
    return eb_render(request, templates_to_try, context)

def schema_detail_special_report(request, schema):
    """
    For display of schemas where is_special_report=True.
    """
    ni_list = NewsItem.objects.filter(schema__id=schema.id)
    populate_schema(ni_list, schema)
    populate_attributes_if_needed(ni_list, [schema])

    if schema.allow_charting:
        browsable_locationtype_list = LocationType.objects.filter(is_significant=True)
        schemafield_list = list(schema.schemafield_set.filter(is_filter=True).order_by('display_order'))
    else:
        browsable_locationtype_list = []
        schemafield_list = []

    templates_to_try = ('db/schema_detail/%s.html' % schema.slug, 'db/schema_detail_special_report.html')
    return eb_render(request, templates_to_try, {
        'schema': schema,
        'newsitem_list': ni_list,
        'browsable_locationtype_list': browsable_locationtype_list,
        'schemafield_list': schemafield_list,
        'bodyclass': 'schema-detail-special-report',
        'bodyid': schema.slug,
    })


def schema_filter_geojson(request, slug, args_from_url):
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
    except FilterError:
        return HttpResponse(status=400)
    except BadAddressException:
        return HttpResponse(status=400)
    except BadDateException:
        return HttpResponse(status=400)

    if filters_need_more:
        return HttpResponse(status=400)


    # If there isn't a date filter, add some dates to the queryset,
    # but NOT to the filterchain, because need to give the user the
    # option of choosing dates.
    qs, start_date, end_date = _default_date_filtering(filterchain)

    if s.is_event:
        qs = qs.order_by('item_date', 'id')
    else:
        qs = qs.order_by('-item_date', '-id')

    page = request.GET.get('page', None)
    if page is not None:
        try:
            page = int(page)
            idx_start = (page - 1) * constants.FILTER_PER_PAGE
            idx_end = page * constants.FILTER_PER_PAGE
            # Get one extra, so we can tell whether there's a next page.
            idx_end += 1
        except ValueError:
            return HttpResponse('Invalid Page', status=400)
    else:
        idx_start, idx_end = 0, 1000
    qs = qs[idx_start:idx_end]

    cache_key = 'schema_filter_geojson:' + _make_cache_key_from_queryset(qs)
    cache_seconds = 60 * 5
    output = cache.get(cache_key, None)
    if output is None:
        output = api_items_geojson(list(qs))
        cache.set(cache_key, output, cache_seconds)

    response = HttpResponse(output, mimetype="application/javascript")
    patch_response_headers(response, cache_timeout=60 * 5)
    return response

def schema_filter(request, slug, args_from_url):
    """
    List NewsItems for one schema, filtered by various criteria in the
    URL (date, location, or values of SchemaFields).
    """
    s = get_object_or_404(get_schema_manager(request), slug=slug, is_special_report=False)
    if not s.allow_charting:
        return HttpResponsePermanentRedirect(s.url())

    context = {
        'bodyclass': 'schema-filter',
        'bodyid': s.slug,
        'schema': s,
        }
    # Breadcrumbs. We can assign this early because it's a generator,
    # so it'll get the full context no matter what.
    context['breadcrumbs'] = breadcrumbs.schema_filter(context)

    filter_sf_list = list(SchemaField.objects.filter(schema__id=s.id, is_filter=True).order_by('display_order'))
    textsearch_sf_list = list(SchemaField.objects.filter(schema__id=s.id, is_searchable=True).order_by('display_order'))

    # Use SortedDict to preserve the display_order.
    filter_sf_dict = SortedDict([(sf.name, sf) for sf in filter_sf_list] + [(sf.name, sf) for sf in textsearch_sf_list])

    # Determine what filters to apply, based on path and/or query string.
    filterchain = FilterChain(request=request, context=context, schema=s)
    context['filters'] = filterchain
    try:
        filterchain.update_from_request(args_from_url, filter_sf_dict)
        filters_need_more = filterchain.validate()
    except FilterError, e:
        if getattr(e, 'url', None) is not None:
            return HttpResponseRedirect(e.url)
        raise Http404(str(e))
    except BadAddressException, e:
        context.update({
                'address_choices': e.address_choices,
                'address': e.address,
                'radius': e.block_radius,
                'radius_slug': e.radius_slug,
                })
        return eb_render(request, 'db/filter_bad_address.html', context)
    except BadDateException, e:
        raise Http404('<h1>%s</h1>' % str(e))

    if filters_need_more:
        # Show a page to select the unspecified value.
        context.update(filters_need_more)
        return eb_render(request, 'db/filter_lookup_list.html', context)

    # Normalize the URL, and redirect if we're not already there.
    new_url = filterchain.make_url()
    if new_url != request.get_full_path():
        return HttpResponseRedirect(new_url)

    # Make the queryset, with default date filtering if needed.
    qs, start_date, end_date = _default_date_filtering(filterchain)

    if s.is_event:
        qs = qs.order_by('item_date', 'id')
    else:
        qs = qs.order_by('-item_date', '-id')

    context['newsitem_qs'] = qs

    #########################################################################

    # Get the list of top values for each lookup that isn't being filtered-by.
    # LOOKUP_MIN_DISPLAYED sets the number of records to display for each lookup
    # type. Normally, the UI displays a "See all" link, but the link is removed
    # if there are fewer than (LOOKUP_MIN_DISPLAYED + LOOKUP_BUFFER) records.
    LOOKUP_MIN_DISPLAYED = 7
    LOOKUP_BUFFER = 4
    lookup_list, boolean_lookup_list, search_list = [], [], []
    for sf in filter_sf_dict.values():
        if sf.is_searchable:
            search_list.append(sf)
        elif sf.is_type('bool'):
            boolean_lookup_list.append(sf)
        elif sf.is_lookup:
            top_values = AggregateFieldLookup.objects.filter(schema_field__id=sf.id).select_related('lookup').order_by('-total')[:LOOKUP_MIN_DISPLAYED+LOOKUP_BUFFER]
            top_values = list(top_values)
            if len(top_values) == LOOKUP_MIN_DISPLAYED + LOOKUP_BUFFER:
                top_values = top_values[:LOOKUP_MIN_DISPLAYED]
                has_more = True
            else:
                has_more = False
            # Note we ordered by -total to get the top values, but since we don't
            # display the count, that ordering is nonsensical to the user.
            top_values = sorted(top_values, key = lambda x: x.lookup.name)
            lookup_list.append({'sf': sf, 'top_values': top_values, 'has_more': has_more})

    # Get the list of LocationTypes if a location filter has *not* been applied.
    if 'location' in filterchain:
        location_type_list = []
    else:
        location_type_list = LocationType.objects.filter(is_significant=True).order_by('slug')

    # Pagination.
    # We don't use Django's Paginator class because it uses
    # SELECT COUNT(*), which we want to avoid.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        raise Http404('Invalid page')

    idx_start = (page - 1) * constants.FILTER_PER_PAGE
    idx_end = page * constants.FILTER_PER_PAGE
    # Get one extra, so we can tell whether there's a next page.
    ni_list = list(qs[idx_start:idx_end+1])
    if page > 1 and not ni_list:
        raise Http404('No objects on page %s' % page)
    if len(ni_list) > constants.FILTER_PER_PAGE:
        has_next = True
        ni_list = ni_list[:-1]
    else:
        has_next = False
        idx_end = idx_start + len(ni_list)
    has_previous = page > 1

    populate_schema(ni_list, s)
    populate_attributes_if_needed(ni_list, [s])

    # Need map parameters based on location/block, if there is one.
    loc_filter = filterchain.get('location')
    if loc_filter:
        context.update(get_place_info_for_request(
                request,
                place=loc_filter.location_object,
                block_radius=getattr(loc_filter, 'block_radius', None)))
    else:
        # Whole city map.
        context.update({
                'default_lon': settings.DEFAULT_MAP_CENTER_LON,
                'default_lat': settings.DEFAULT_MAP_CENTER_LAT,
                'default_zoom': settings.DEFAULT_MAP_ZOOM,
                })

    # Try to provide a link to larger map, but don't worry about it
    # if there is no richmap app hooked in...
    try:
        large_map_url = filterchain.make_url(base_url=reverse('bigmap_filter', args=(slug,)))
        if filterchain.get('date') is None:
            # force a date range
            large_map_url += '?end_date=' + ni_list[0].pub_date.strftime("%m/%d/%Y") 

        context.update({
            'large_map_url': large_map_url
        })
    except:
        pass

    context.update({
        'newsitem_list': ni_list,

        # Pagination stuff
        'has_next': has_next,
        'has_previous': has_previous,
        'page_number': page,
        'previous_page_number': page - 1,
        'next_page_number': page + 1,
        'page_start_index': idx_start + 1,
        'page_end_index': idx_end,
        'lookup_list': lookup_list,
        'boolean_lookup_list': boolean_lookup_list,
        'search_list': search_list,
        'location_type_list': location_type_list,
        'date_filter_applied': filterchain.has_key('date'),
        'location_filter_applied': filterchain.has_key('location'),
        'lookup_descriptions': filterchain.lookup_descriptions,
        'start_date': start_date,
        'end_date': end_date,
    })
    context['map_configuration'] = _preconfigured_map(context);

    return eb_render(request, 'db/filter.html', context)


def _default_date_filtering(filterchain):
    """
    Make sure we do some date limiting, but don't force a
    DateFilter into the filterchain, because that would prevent
    users from choosing dates.
    """
    schema = filterchain['schema'].schema
    date_filter = filterchain.get('date') or filterchain.get('pubdate')
    qs = filterchain.apply()
    if date_filter:
        start_date = date_filter.start_date
        end_date = date_filter.end_date
    else:
        if schema.is_event:
            start_date = today()
            end_date = start_date + datetime.timedelta(days=30)
        else:
            start_date = schema.min_date
            end_date = today()
        qs = qs.filter(item_date__gte=start_date,
                       item_date__lte=end_date)
    return qs, start_date, end_date

def location_type_list(request):
    """
    Default view of /locations; just redirect to the default loc type.
    """
    url = reverse('ebpub-loc-type-detail', args=(settings.DEFAULT_LOCTYPE_SLUG,))
    return HttpResponsePermanentRedirect(url)

def location_type_detail(request, slug):
    lt = get_object_or_404(LocationType, slug=slug)
    order_by = get_metro()['multiple_cities'] and ('city', 'display_order') or ('display_order',)
    loc_list = Location.objects.filter(location_type__id=lt.id, is_public=True).order_by(*order_by)
    lt_list = [{'location_type': i, 'is_current': i == lt} for i in LocationType.objects.filter(is_significant=True).order_by('plural_name')]
    context = {
        'location_type': lt,
        'location_list': loc_list,
        'location_type_list': lt_list,
        'bodyclass': 'location-type-detail',
        'bodyid': slug,
        }
    context['breadcrumbs'] = breadcrumbs.location_type_detail(context)
    return eb_render(request, 'db/location_type_detail.html', context)


def city_list(request):
    city_type_slug = get_metro()['city_location_type']
    cities_with_streets = set([City.from_norm_name(c['city']).slug
                               for c in Street.objects.order_by().distinct().values('city')])
    all_cities = [City.from_norm_name(v['slug']) for v in
                  Location.objects.filter(location_type__slug=city_type_slug).values('slug', 'name').order_by('name')]

    all_cities = [city for city in all_cities if city.slug.strip()]
    return eb_render(request, 'db/city_list.html',
                     {'all_cities': all_cities,
                      'cities_with_streets': cities_with_streets,
                      'bodyclass': 'city-list',
                      })

def street_list(request, city_slug):
    city = city_slug and City.from_slug(city_slug) or None
    kwargs = city_slug and {'city': city.norm_name} or {}
    streets = list(Street.objects.filter(**kwargs).order_by('street', 'suffix'))
    if not streets:
        raise Http404('This city has no streets')
    context = {
        'street_list': streets,
        'city': city,
        'bodyclass': 'street-list',
        'example_loctype': LocationType.objects.get(slug=settings.DEFAULT_LOCTYPE_SLUG).plural_name,
    }
    context['breadcrumbs'] = breadcrumbs.street_list(context)
    return eb_render(request, 'db/street_list.html', context)

def block_list(request, city_slug, street_slug):
    city = city_slug and City.from_slug(city_slug) or None
    kwargs = {'street_slug': street_slug}
    if city_slug:
        city_filter = Q(left_city=city.norm_name) | Q(right_city=city.norm_name)
    else:
        city_filter = Q()
    blocks = Block.objects.filter(city_filter, **kwargs).order_by('postdir', 'predir', 'from_num', 'to_num')
    if not blocks:
        raise Http404('This street has no blocks')
    context = {
        'block_list': blocks,
        'first_block': blocks[0],
        'city': city,
        'bodyclass': 'block-list',
    }
    context['breadcrumbs'] = breadcrumbs.block_list(context)
    return eb_render(request, 'db/block_list.html', context)


def _place_detail_normalize_url(request, *args, **kwargs):
    context = get_place_info_for_request(request, *args, **kwargs)
    if context.get('block_radius') and 'radius' not in request.GET:
        # Normalize the URL so we always have the block radius.
        url = request.get_full_path()
        response = HttpResponse(status=302)
        if '?' in url:
            response['location'] = '%s&radius=%s' % (url, context['block_radius'])
        else:
            response['location'] = '%s?radius=%s' % (url, context['block_radius'])
        for key, val in context.get('cookies_to_set').items():
            response.set_cookie(key, val)
        return (context, response)
    return (context, None)


def place_detail_timeline(request, *args, **kwargs):
    """
    Recent news OR upcoming events for the given Location or Block.
    """
    context, response = _place_detail_normalize_url(request, *args, **kwargs)
    if response is not None:
        return response

    show_upcoming = kwargs.get('show_upcoming')
    schema_manager = get_schema_manager(request)

    if show_upcoming:
        context['breadcrumbs'] = breadcrumbs.place_detail_upcoming(context)
    else:
        context['breadcrumbs'] = breadcrumbs.place_detail_timeline(context)

    is_latest_page = True
    # Check the query string for the max date to use. Otherwise, fall
    # back to today.
    end_date = today()
    if 'start' in request.GET:
        try:
            end_date = parse_date(request.GET['start'], '%m/%d/%Y')
            is_latest_page = False
        except ValueError:
            raise Http404('Invalid date %s' % request.GET['start'])

    filterchain = FilterChain(request=request, context=context)
    filterchain.add('location', context['place'])
    # As an optimization, limit the NewsItems to those on the
    # last (or next) few days.
    # And only fetch for relevant schemas - either event-ish or not.
    if show_upcoming:
        s_list = schema_manager.filter(is_event=True)
        start_date = end_date
        end_date = start_date + datetime.timedelta(days=settings.DEFAULT_DAYS)
        order_by = 'item_date_date'
    else:
        s_list = schema_manager.filter(is_event=False)
        start_date = end_date - datetime.timedelta(days=settings.DEFAULT_DAYS)
        order_by = '-item_date_date'

    filterchain.add('schema', list(s_list))
    filterchain.add('date', start_date, end_date)
    newsitem_qs = filterchain.apply().select_related()
    # TODO: can this really only be done via extra()?
    newsitem_qs = newsitem_qs.extra(
        select={'item_date_date': 'date(db_newsitem.item_date)'},
        order_by=(order_by, '-schema__importance', 'schema')
    )[:constants.NUM_NEWS_ITEMS_PLACE_DETAIL]

    # We're done filtering, so go ahead and do the query, to
    # avoid running it multiple times,
    # per http://docs.djangoproject.com/en/dev/topics/db/optimization
    ni_list = list(newsitem_qs)
    schemas_used = list(set([ni.schema for ni in ni_list]))
    s_list = s_list.filter(is_special_report=False, allow_charting=True).order_by('plural_name')
    populate_attributes_if_needed(ni_list, schemas_used)
    if ni_list:
        next_day = ni_list[-1].item_date - datetime.timedelta(days=1)
    else:
        next_day = None

    hidden_schema_list = []
    if not request.user.is_anonymous():
        hidden_schema_list = [o.schema for o in HiddenSchema.objects.filter(user_id=request.user.id)]

    context.update({
        'newsitem_list': ni_list,
        'next_day': next_day,
        'is_latest_page': is_latest_page,
        'hidden_schema_list': hidden_schema_list,
        'bodyclass': 'place-detail-timeline',
        'bodyid': context.get('place_type') or '',
        'filters': filterchain,
        'show_upcoming': show_upcoming,
    })


    context['filtered_schema_list'] = s_list
    context['map_configuration'] = _preconfigured_map(context);
    response = eb_render(request, 'db/place_detail.html', context)
    for k, v in context['cookies_to_set'].items():
        response.set_cookie(k, v)
    return response

def _preconfigured_map(context):
    """
    helper to rig up a map configuration for 
    templates based on the menagerie of
    values provided in the template context.
    
    returns a json string with the layer configuration 
    for the map that should be displayed on the page. 
    """
    
    config = {
        'locations': [],
        'layers': [],
    }

    # load layer boundary if a Location is specified
    location = context.get('location')
    if location is not None:
        loc_json_url = reverse('location_detail_json',
                                 kwargs={'loctype': location.location_type.slug, 
                                         'slug': location.slug})
        loc_boundary = {
            'url': loc_json_url,
            'params': {},
            'title': "%s Boundary" % location.pretty_name,
            'visible': True
        }
        config['locations'].append(loc_boundary);

    ###########################
    # configure newsitem layer 
    # 
    # TODO filtering? via api? see ticket #121
    ###########################
    
    filters = context.get('filters', None)
    if filters is not None and (filters.schema is not None and not isinstance(filters.schema, list)):
        base_url = reverse('ebpub-schema-filter-geojson', args=(context['schema'].slug,))
        layer_url = filters.make_url(base_url=base_url)
        layer_params = {}
        if 'page_number' in context: 
            layer_params['page'] = context['page_number']
        items_layer = {
            'url': layer_url,
            'params': layer_params,
            'title': "Custom Filter" ,
            'visible': True
        }
    else:
        # make up an api layer from the context 
    
        # single news item ? 
        layer_params = {}
        item = context.get('newsitem')
        if item is not None: 
            layer_params['newsitem'] = item.id

        # restricted to place?
        for key in ['pid']:
            val = context.get(key)
            if val is not None: 
                layer_params[key] = val

        # restricted date range ?
        for key in ['start_date', 'end_date']:
            val = context.get(key)
            if val is not None: 
                layer_params[key] = val.strftime('%Y/%m/%d')

        # restricted by schema ?
        schema_slug = context.get('schema_slug')
        if schema_slug is not None: 
            layer_params['schema'] = schema_slug

        items_layer = {
            'url': reverse('ajax-newsitems-geojson'),
            'params': layer_params,
            'title': "News" ,
            'visible': True
        }
    config['layers'].append(items_layer)
    config['baselayer_type'] = settings.MAP_BASELAYER_TYPE
    return simplejson.dumps(config, indent=2)



def place_detail_overview(request, *args, **kwargs):
    context, response = _place_detail_normalize_url(request, *args, **kwargs)
    if response is not None:
        return response
    schema_manager = get_schema_manager(request)
    context['breadcrumbs'] = breadcrumbs.place_detail_overview(context)

    schema_list = SortedDict([(s.id, s) for s in schema_manager.filter(is_special_report=False).order_by('plural_name')])
    # needed = set(schema_list.keys())

    # We actually want two lists of schemas, since we care whether
    # they are news-like or future-event-like.
    import copy
    eventish_schema_list = copy.deepcopy(schema_list)
    newsish_schema_list = copy.deepcopy(schema_list)
    for s_id, schema in schema_list.items():
        if schema.is_event:
            del(newsish_schema_list[s_id])
        else:
            del(eventish_schema_list[s_id])

    filterchain = FilterChain(request=request, context=context)
    filterchain.add('location', context['place'])

    # Distinguish between past news and upcoming events.
    # With some preliminary date limiting too.
    filterchain_news = filterchain.copy()
    filterchain_news.add('date',
                         today() - datetime.timedelta(days=90),
                         today())

    filterchain_events = filterchain.copy()
    filterchain_events.add('date',
                           today(),
                           today() + datetime.timedelta(days=60))

    # Ordering by ID ensures consistency across page views.
    newsitem_qs = filterchain_news.apply().order_by('-item_date', '-id')
    events_qs = filterchain_events.apply().order_by('item_date', 'id')

    # Mapping of schema id -> [schemafields], for building Lookup charts.
    sf_dict = {}
    charted_lookups = SchemaField.objects.filter(
        is_lookup=True, is_charted=True, schema__is_public=True,
        schema__is_special_report=False)
    charted_lookups = charted_lookups.values('id', 'schema_id', 'pretty_name')
    for sf in charted_lookups.order_by('schema__id', 'display_order'):
        sf_dict.setdefault(sf['schema_id'], []).append(sf)

    # Now retrieve newsitems per schema.
    schema_groups, all_newsitems = [], []
    for schema in schema_list.values():
        if schema.id in newsish_schema_list:
            newsitems = newsitem_qs.filter(schema__id=schema.id)
        elif schema.id in eventish_schema_list:
            newsitems = events_qs.filter(schema__id=schema.id)
        else:
            raise RuntimeError("should never get here")
        newsitems = list(newsitems[:s.number_in_overview])
        populate_schema(newsitems, schema)
        schema_groups.append({
            'schema': schema,
            'latest_newsitems': newsitems,
            'has_newsitems': bool(newsitems),
            'lookup_charts': sf_dict.get(schema.id),
        })
        all_newsitems.extend(newsitems)
    schema_list = schema_list.values()
    populate_attributes_if_needed(all_newsitems, schema_list)
    schema_list = [s for s in schema_list if s.allow_charting]

    context['schema_groups'] = schema_groups
    context['filtered_schema_list'] = schema_list
    context['bodyclass'] = 'place-detail-overview'
    if context['is_block']:
        context['bodyid'] = '%s-%s-%s' % (context['place'].street_slug,
                                          context['place'].number(),
                                          context['place'].dir_url_bit())
    else:
        context['bodyid'] = context['location'].slug
    response = eb_render(request, 'db/place_overview.html', context)
    for k, v in context['cookies_to_set'].items():
        response.set_cookie(k, v)
    return response


def feed_signup(request, *args, **kwargs):
    context = get_place_info_for_request(request, *args, **kwargs)
    context['schema_list'] = get_schema_manager(request).filter(is_special_report=False).order_by('plural_name')
    context['map_configuration'] = _preconfigured_map(context);
    return eb_render(request, 'db/feed_signup.html', context)

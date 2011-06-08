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
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from ebpub.db.models import Location
from ebpub.streets.models import Block
from ebpub.streets.models import City
from ebpub.metros.allmetros import get_metro
from ebpub.constants import BLOCK_RADIUS_CHOICES, BLOCK_RADIUS_DEFAULT
from ebpub.constants import BLOCK_RADIUS_COOKIE_NAME
from ebpub.utils.view_utils import make_pid
from ebpub.savedplaces.models import SavedPlace
import datetime

def smart_bunches(newsitem_list, max_days=5, max_items_per_day=100):
    """
    Helper function that takes a list of NewsItems, ordered descending by
    pub_date, and returns a list of NewsItems that's been optimized for
    display in timelines.

    Assumes each NewsItem has a pub_date_date attribute!

    The logic is:
        * Go backwards in time until there are 5 full days' worth of news
          (not necessarily 5 consecutive days).
        * If, for any day, there are more than 100 items, stop at that day
          (inclusive).
        * Any NewsItems in the list with a pub_date equal to the oldest
          pub_date in the list will be removed. This is because we cannot
          assume *all* of the items with that pub_date are in the list.
    """
    if newsitem_list:
        current_date = None
        days_seen = 0
        stop_at_next_day = False
        end_index = None
        oldest_pub_date = newsitem_list[-1].pub_date_date
        for i, ni in enumerate(newsitem_list):
            if ni.pub_date_date != current_date:
                days_seen += 1
                current_date = ni.pub_date_date
                items_in_current_day = 1
                if stop_at_next_day or days_seen > max_days or ni.pub_date_date == oldest_pub_date:
                    end_index = i
                    break
            else:
                items_in_current_day += 1
                if items_in_current_day > max_items_per_day:
                    stop_at_next_day = True
        if end_index is not None:
            del newsitem_list[end_index:]
    return newsitem_list

def populate_attributes_if_needed(newsitem_list, schema_list):
    """
    Helper function that takes a list of NewsItems and sets ni.attribute_values
    to a dictionary of attributes {field_name: value} for all NewsItems whose
    schemas have uses_attributes_in_list=True. This is accomplished with a
    minimal amount of database queries.

    The values in the attribute_values dictionary are Lookup instances in the
    case of Lookup fields. Otherwise, they're the direct values from the
    Attribute table.

    schema_list should be a list of all Schemas that are referenced in
    newsitem_list.

    Note that the list is edited in place; there is no return value.
    """
    from ebpub.db.models import Attribute, Lookup, SchemaField
    # To accomplish this, we determine which NewsItems in ni_list require
    # attribute prepopulation, and run a single DB query that loads all of the
    # attributes. Another way to do this would be to load all of the attributes
    # when loading the NewsItems in the first place (via a JOIN), but we want
    # to avoid joining such large tables.

    # TODO: #72. This is an optimization that doesn't justify having a
    # parallel API that isn't even documented in model code where it
    # belongs. Rewrite to stuff the data in ni._attributes_cache
    # instead.

    preload_schema_ids = set([s.id for s in schema_list if s.uses_attributes_in_list])
    if not preload_schema_ids:
        return
    preloaded_nis = [ni for ni in newsitem_list if ni.schema_id in preload_schema_ids]
    if not preloaded_nis:
        return
    # fmap is a mapping like:
    # {schema_id: {'fields': [(name, real_name)], 'lookups': [real_name1, real_name2]}}
    fmap = {}
    attribute_columns_to_select = set(['news_item'])

    for sf in SchemaField.objects.filter(schema__id__in=[s.id for s in schema_list]).values('schema', 'name', 'real_name', 'is_lookup'):
        fmap.setdefault(sf['schema'], {'fields': [], 'lookups': []})['fields'].append((sf['name'], sf['real_name']))
        if sf['is_lookup']:
            fmap[sf['schema']]['lookups'].append(sf['real_name'])
        attribute_columns_to_select.add(str(sf['real_name']))

    att_dict = dict([(i['news_item'], i) for i in Attribute.objects.filter(news_item__id__in=[ni.id for ni in preloaded_nis]).values(*list(attribute_columns_to_select))])

    if not fmap: 
        return

    # Determine which Lookup objects need to be retrieved.
    lookup_ids = set()
    for ni in preloaded_nis:
        # Fix for #38: not all Schemas have SchemaFields, can be 100% vanilla.
        if not ni.schema_id in fmap:
            continue
        for real_name in fmap[ni.schema_id]['lookups']:
            value = att_dict[ni.id][real_name]
            if ',' in str(value):
                lookup_ids.update(value.split(','))
            else:
                lookup_ids.add(value)

    # Retrieve only the Lookups that are referenced in preloaded_nis.
    lookup_ids = [i for i in lookup_ids if i]
    if lookup_ids:
        lookup_objs = Lookup.objects.in_bulk(lookup_ids)
    else:
        lookup_objs = {}
        
    # Set 'attribute_values' for each NewsItem in preloaded_nis.
    for ni in preloaded_nis:
        if not ni.id in att_dict:
            # Fix for #38: Schemas may not have any SchemaFields, and
            # thus the ni will have no attributes, and that's OK.
            continue
        att = att_dict[ni.id]
        att_values = {}
        for field_name, real_name in fmap[ni.schema_id]['fields']:
            value = att[real_name]
            if real_name in fmap[ni.schema_id]['lookups']:
                if real_name.startswith('int'):
                    value = lookup_objs[value]
                else: # Many-to-many lookups are comma-separated strings.
                    value = [lookup_objs[int(i)] for i in value.split(',') if i]
            att_values[field_name] = value
        ni.attribute_values = att_values

def populate_schema(newsitem_list, schema):
    for ni in newsitem_list:
        # TODO: This relies on undocumented Django APIs -- the "_schema_cache" name.
        ni._schema_cache = schema

def today():
    if settings.EB_TODAY_OVERRIDE:
        return settings.EB_TODAY_OVERRIDE
    return datetime.date.today()

def get_locations_near_place(place, block_radius=3):
    nearby = Location.objects.filter(location_type__is_significant=True)
    nearby = nearby.select_related()
    if isinstance(place, Location):
        nearby = nearby.exclude(id=place.id)
    # If the location is a point, or very small, we want to expand
    # the area we care about via make_search_buffer().  But if
    # it's not, we probably want the extent of its geometry.
    # Let's just take the union to cover both cases.
    search_buf = make_search_buffer(place.location.centroid, block_radius)
    search_buf = search_buf.union(place.location)
    nearby = nearby.filter(location__bboverlaps=search_buf)
    nearby = nearby.order_by('location_type__id', 'name')
    return nearby, search_buf

def get_place_info_for_request(request, *args, **kwargs):
    """
    A utility function that abstracts getting some commonly used
    location-related information: a place (Location or Block), its type,
    a bbox, a list of nearby locations, etc.
    """
    info = dict(bbox=None,
                nearby_locations=[],
                location=None,
                place_type=None,
                is_block=False,
                block_radius=None,
                is_saved=False,
                pid='',
                cookies_to_set={},
                )

    if 'place' in kwargs:
        info['place'] = place = kwargs['place']
    else:
        info['place'] = place = url_to_place(*args, **kwargs)

    if isinstance(place, Block):
        info['is_block'] = True
        xy_radius, block_radius, cookies_to_set = block_radius_value(request)
        block_radius = kwargs.get('block_radius') or block_radius
        nearby, search_buf = get_locations_near_place(place, block_radius)
        info['nearby_locations'] = nearby
        info['bbox'] = search_buf.extent
        saved_place_lookup = {'block__id': place.id}
        info['block_radius'] = block_radius
        info['cookies_to_set'] = cookies_to_set
        info['pid'] = make_pid(place, block_radius)
        info['place_type'] = 'block'
    else:
        info['location'] = place
        info['place_type'] = place.location_type.slug
        saved_place_lookup = {'location__id': place.id}
        info['pid'] = make_pid(place)
        if place.location is None:
            # No geometry.
            info['bbox'] = get_metro()['extent']
        else:
            nearby, search_buf = get_locations_near_place(place)
            info['bbox'] = search_buf.extent
            info['nearby_locations'] = nearby

    # Determine whether this is a saved place.
    if not request.user.is_anonymous():
        saved_place_lookup['user_id'] = request.user.id # TODO: request.user.id should not do a DB lookup
        info['is_saved'] = SavedPlace.objects.filter(**saved_place_lookup).count()

    return info

def url_to_place(*args, **kwargs):
    # Given args and kwargs captured from the URL, returns the place.
    # This relies on "place_type" being provided in the URLpattern.
    parse_func = kwargs['place_type'] == 'block' and url_to_block or url_to_location
    return parse_func(*args)

def url_to_block(city_slug, street_slug, from_num, to_num, predir, postdir):
    params = {
        'street_slug': street_slug,
        'predir': (predir and predir.upper() or ''),
        'postdir': (postdir and postdir.upper() or ''),
        'from_num': int(from_num),
        'to_num': int(to_num),
    }
    if city_slug:
        city = City.from_slug(city_slug).norm_name
        city_filter = Q(left_city=city) | Q(right_city=city)
    else:
        city_filter = Q()
    b_list = list(Block.objects.filter(city_filter, **params))

    if not b_list:
        raise Http404()

    return b_list[0]

def url_to_location(type_slug, slug):
    return get_object_or_404(Location.objects.select_related(), location_type__slug=type_slug, slug=slug)


def block_radius_value(request):
    """
    Get block radius from either query string or cookie, or default.
    """
    # Returns a tuple of (xy_radius, block_radius, cookies_to_set).
    if 'radius' in request.GET and request.GET['radius'] in BLOCK_RADIUS_CHOICES:
        block_radius = request.GET['radius']
        cookies_to_set = {BLOCK_RADIUS_COOKIE_NAME: block_radius}
    else:
        if request.COOKIES.get(BLOCK_RADIUS_COOKIE_NAME) in BLOCK_RADIUS_CHOICES:
            block_radius = request.COOKIES[BLOCK_RADIUS_COOKIE_NAME]
        else:
            block_radius = BLOCK_RADIUS_DEFAULT
        cookies_to_set = {}
    return BLOCK_RADIUS_CHOICES[block_radius], block_radius, cookies_to_set

def make_search_buffer(geom, block_radius):
    """
    Returns a polygon of a buffer around a block's centroid. `geom'
    should be the centroid of the block. `block_radius' is number of
    blocks.
    """
    return geom.buffer(BLOCK_RADIUS_CHOICES[str(block_radius)]).envelope

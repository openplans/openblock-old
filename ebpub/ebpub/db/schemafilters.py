#   Copyright 2011 Everyblock LLC, OpenPlans, and contributors
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

"""
API that abstracts filtering NewsItems by various criteria.
Features:

* validation of filter parameters.
* detecting when more user input is needed, so views can provide a
  disambiguation UI.
* consistent normalized URLs and breadcrumbs.
* consistent order of filter application

TODO:
 *  generate URLs for the REST API too?

 *  profile optimal order of filters for sort()?
    Currently guessing it should be something like:
    schema, date, non-lookup attrs, block/location, lookup attrs, text search.
    This will need profiling with lots of test data.
"""

from django.utils import dateformat
from django.utils.datastructures import SortedDict
from ebpub.db import constants
from ebpub.db import models
from ebpub.db.utils import block_radius_value
from ebpub.db.utils import make_search_buffer
from ebpub.db.utils import url_to_block
from ebpub.db.utils import url_to_location
from ebpub.geocoder import SmartGeocoder, AmbiguousResult, GeocodingException
from ebpub.geocoder.parser.parsing import ParsingError
from ebpub.metros.allmetros import get_metro
from ebpub.utils.dates import parse_date
from ebpub.utils.view_utils import has_staff_cookie
from ebpub.utils.view_utils import parse_pid

import calendar
import datetime
import ebpub.streets.models
import logging
import re
import urllib

logger = logging.getLogger('ebpub.db.schemafilters')

class NewsitemFilter(object):

    """
    Base class for filtering NewsItems.
    """

    _sort_value = 100.0  # Used by FilterChain for sorting filters.

    # Various attributes used for URL construction, breadcrumbs,
    # and for display in templates.
    # If these are None, they should not be shown to the user.

    slug = None   # ID for this type of filter. Used with FilterChain.add() / .remove()
    url = None  # Actually a URL fragment.
    value = None  # Value fed to the filter, for display.
    label = None  # Human-readable name of the filter, for display.
    short_value = None  # Shorter version of value fed to the filter, for display.

    def __init__(self, request, context, queryset=None, *args, **kw):
        self.qs = queryset if (queryset is not None) else models.NewsItem.objects.all()
        self.context = context
        self.request = request
        self._got_args = False

    def apply(self):
        """mutate the queryset, and any other state that needs sharing
        with others.
        """
        raise NotImplementedError # pragma: no cover

    def validate(self):
        """
        If we didn't get enough info from the args, eg. it's a
        Location filter but no location was specified, then return a
        dict of stuff for putting in a template context.

        If we have enough information, returns an empty dict.

        ... or maybe should be something more generic across both REST
        and UI views
        """
        # TODO: Maybe split this into .get_extra_context() -> dict
        # and .needs_more_info() -> bool
        raise NotImplementedError  # pragma: no cover

    def __getitem__(self, key):
        # Emulate a dict to make legacy code in ebpub.db.breadcrumbs happy
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)


class FilterError(Exception):
    """
    All-purpose exception for invalid filter parameters and the like.

    If self.url is set, it may be used for redirection.
    """
    def __init__(self, msg, url=None):
        self.msg = msg
        self.url = url

    def __str__(self):
        return repr(self.msg)


class SchemaFilter(NewsitemFilter):
    """
    Filters by NewsItem.schema.
    """
    _sort_value = -9999
    slug = 'schema'
    url = None
    label = None  # Don't show this one in the UI.
    value = None

    def __init__(self, request, context, queryset, *args, **kwargs):
        NewsitemFilter.__init__(self, request, context, queryset, *args, **kwargs)
        self.schema = kwargs['schema']

    def validate(self):
        return {}

    def apply(self):
        if isinstance(self.schema, list):
            self.qs = self.qs.filter(schema__in=self.schema)
        else:
            self.qs = self.qs.filter(schema=self.schema)


class AttributeFilter(NewsitemFilter):

    """
    Base class for more specific types of attribute filters
    (LookupFilter, TextSearchFilter, etc).
    """

    _sort_value = 101.0

    def __init__(self, request, context, queryset, *args, **kwargs):
        NewsitemFilter.__init__(self, request, context, queryset, *args, **kwargs)
        self.schemafield = kwargs['schemafield']
        self.slug = self.schemafield.name
        self.argname = 'by-%s' % self.slug
        self.url = 'by-%s=' % self.slug
        self.value = self.short_value = ''
        self.label = self.schemafield.pretty_name
        if args:
            # This should work for int and varchar fields. (TODO: UNTESTED)
            self.att_value = args[0]
            self._got_args = True
            if isinstance(self.att_value, datetime.date):
                str_att_value = self.att_value.strftime('%Y-%m-%d')
            elif isinstance(self.att_value, datetime.time):
                str_att_value = self.att_value.strftime('%H:%M:%S')
            elif isinstance(self.att_value, datetime.datetime):
                # Zone??
                str_att_value = self.att_value.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                str_att_value = str(self.att_value)
            self.url += str_att_value

    def apply(self):
        self.qs = self.qs.by_attribute(self.schemafield, self.att_value)


class TextSearchFilter(AttributeFilter):

    """Does a text search on values of the given attribute.
    """

    _sort_value = 1000.0

    def __init__(self, request, context, queryset, *args, **kwargs):
        AttributeFilter.__init__(self, request, context, queryset, *args, **kwargs)
        self.label = self.schemafield.pretty_name
        if not args:
            raise FilterError('Text search lookup requires search params')
        self.query = ', '.join(args)
        self.short_value = self.query
        self.value = self.query
        self.url = 'by-%s=%s' % (self.schemafield.name, self.query)

    def apply(self):
        self.qs = self.qs.text_search(self.schemafield, self.query)

    def validate(self):
        return {}

class BoolFilter(AttributeFilter):

    """
    Filters on boolean attributes.
    """

    _sort_value = 100.0

    def __init__(self, request, context, queryset, *args, **kwargs):
        AttributeFilter.__init__(self, request, context, queryset, *args, **kwargs)
        if len(args) > 1:
            raise FilterError("Invalid boolean arg %r" % ','.join(args))
        elif len(args) == 1:
            self.boolslug = args[0]
            self.real_val = {'yes': True, 'no': False, 'na': None}.get(self.boolslug, self.boolslug)
            if self.real_val not in (True, False, None):
                raise FilterError('Invalid boolean value %r' % self.boolslug)
            self.url = 'by-%s=%s' % (self.schemafield.name, self.boolslug)
            self._got_args = True
        else:
            # No args.
            self.value = u'By whether they %s' % self.schemafield.pretty_name_plural
            self._got_args = False

    def validate(self):
        if self._got_args:
            return {}
        return {
            'lookup_type': self.value[3:],
            'lookup_type_slug': self.schemafield.name,
            'lookup_list': [{'slug': 'yes', 'name': 'Yes'}, {'slug': 'no', 'name': 'No'}, {'slug': 'na', 'name': 'N/A'}],
            }


    def apply(self):
        self.qs = self.qs.by_attribute(self.schemafield, self.real_val)
        self.short_value = {True: 'Yes', False: 'No', None: 'N/A'}[self.real_val]
        self.value = u'%s%s: %s' % (self.label[0].upper(), self.label[1:], self.short_value)


class LookupFilter(AttributeFilter):
    """
    Filters on Lookup attributes (see ebpub.db.models for more info).

    TODO: currently handles only one lookup value
    """

    _sort_value = 900.0

    def __init__(self, request, context, queryset, *args, **kwargs):
        AttributeFilter.__init__(self, request, context, queryset, *args, **kwargs)
        try:
            slug = args[0]
            self._got_args = True
        except IndexError:
            self._got_args = False
            self.look = None
        if self._got_args:
            if isinstance(slug, models.Lookup):
                self.look = slug
                slug = self.look.slug
            else:
                try:
                    self.look = models.Lookup.objects.get(
                        schema_field__id=self.schemafield.id, slug=slug)
                except models.Lookup.DoesNotExist:
                    raise FilterError("No such lookup %r" % slug)
            self.value = self.look.name
            self.short_value = self.value
            self.url = 'by-%s=%s' % (self.schemafield.name, slug)

    def validate(self):
        if self._got_args:
            return {}
        lookup_list = models.Lookup.objects.filter(schema_field__id=self.schemafield.id).order_by('name')
        return {
            'lookup_type': self.schemafield.pretty_name,
            'lookup_type_slug': self.schemafield.name,
            'lookup_list': lookup_list,
        }

    def apply(self):
        self.qs = self.qs.by_attribute(self.schemafield, self.look, is_lookup=True)


class LocationFilter(NewsitemFilter):

    """
    Filters on intersecting ebpub.db.models.Location.
    """

    _sort_value = 200.0

    slug = 'location'

    def __init__(self, request, context, queryset, *args, **kwargs):
        NewsitemFilter.__init__(self, request, context, queryset, *args, **kwargs)
        self.location_object = None
        if 'location' in kwargs:
            self._update_location(kwargs['location'])
            self._got_args = True
        else:
            if 'location_type' in kwargs:
                self.location_type = kwargs['location_type']
                self.location_type_slug = self.location_type.slug
                self.label = self.location_type.name
            else:
                if not args:
                    raise FilterError("not enough args")
                self.location_type_slug = args[0]
            self.url = 'locations=%s' % self.location_type_slug
            self.value = 'Choose %s' % self.location_type_slug.title()
            try:
                self.location_slug = args[1]
                self._got_args = True
            except IndexError:
                self._got_args = False

        if self._got_args and self.location_object is None:
            loc = url_to_location(self.location_type_slug, self.location_slug)
            self._update_location(loc)

    def _update_location(self, loc):
        self.location_slug = loc.slug
        self.location_type = loc.location_type
        self.location_type_slug = loc.location_type.slug
        self.label = loc.location_type.name
        self.short_value = loc.name
        self.value = loc.name
        self.url = 'locations=%s,%s' % (self.location_type_slug, self.location_slug)
        self.location_name = loc.name
        self.location_object = loc

    def validate(self):
        # List of available locations for this location type.
        if self._got_args:
            return {}
        else:
            lookup_list = models.Location.objects.filter(location_type__slug=self.location_type_slug, is_public=True).order_by('display_order')
            if not lookup_list:
                raise FilterError("empty lookup list")
            location_type = lookup_list[0].location_type
            return {
                'lookup_type': location_type.name,
                'lookup_type_slug': self.location_type_slug,
                'lookup_list': lookup_list,
                }


    def apply(self):
        """
        filtering by Location
        """
        loc = self.location_object
        self.qs = self.qs.filter(newsitemlocation__location__id=loc.id)


class BlockFilter(NewsitemFilter):

    """
    Filters on intersecting ebpub.streets.models.Block.
    """
    slug = 'location'

    _sort_value = 200.0

    def _update_block(self, block):
        self.location_object = self.context['place'] = block
        self.city_slug = block.city  # XXX is that a slug?
        self.street_slug = block.street_slug
        self.block_range = block.number() + block.dir_url_bit()
        self.label = 'Area'
        # Assume we already have self.block_radius.
        value = '%s block%s around %s' % (self.block_radius, (self.block_radius != '1' and 's' or ''), block.pretty_name)
        self.short_value = value
        self.value = value
        self.url = 'streets='
        if get_metro()['multiple_cities']:
            self.url += self.city_slug + ','
        self.url += '%s,%s%s,%s' % (block.street_slug,
                                    block.number(), block.dir_url_bit(),
                                    radius_slug(self.block_radius))
        self.location_name = block.pretty_name


    def __init__(self, request, context, queryset, *args, **kwargs):
        NewsitemFilter.__init__(self, request, context, queryset, *args, **kwargs)
        self.location_object = None
        args = list(args)

        if 'block' not in kwargs:
            # We do this first so we consume the right number of args
            # before getting to block_radius.
            try:
                if get_metro()['multiple_cities']:
                    self.city_slug = args.pop(0)
                else:
                    self.city_slug = ''
                self.street_slug = args.pop(0)
                self.block_range = args.pop(0)
            except IndexError:
                raise FilterError("not enough args")

        try:
            block_radius = args.pop(0)
            self.block_radius = radius_from_slug(block_radius)
        except (TypeError, ValueError):
            raise FilterError('bad radius %r' % block_radius)
        except IndexError:
            self.block_radius = context.get('block_radius')
            if self.block_radius is None:
                # Redirect to a URL that includes some radius, either
                # from a cookie, or the default radius.
                # TODO: Filters are used in various contexts, but the
                # redirect URL is tailored only for the schema_filter
                # view.
                xy_radius, block_radius, cookies_to_set = block_radius_value(request)
                radius_url = u'%s,%s/' % (request.path.rstrip('/'),
                                          radius_slug(block_radius))
                raise FilterError('missing radius', url=radius_url)

        if 'block' in kwargs:
            # needs block_radius to already be there.
            self._update_block(kwargs['block'])

        m = re.search('^%s$' % constants.BLOCK_URL_REGEX, self.block_range)
        if not m:
            raise FilterError('Invalid block URL: %r' % self.block_range)
        self.url_to_block_args = m.groups()
        self._got_args = True

        if self.location_object is not None:
            block = self.location_object
        else:
            block = url_to_block(self.city_slug, self.street_slug,
                                 *self.url_to_block_args)
            self._update_block(block)


    def validate(self):
        # Filtering UI does not provide a page for selecting a block.
        return {}

    def apply(self):
        """filtering by Block.
        """
        block = self.location_object
        search_buf = make_search_buffer(block.location.centroid, self.block_radius)
        self.qs = self.qs.filter(location__bboverlaps=search_buf)
        return self.qs


class DateFilter(NewsitemFilter):

    """Filters on NewsItem.item_date.
    The start_date and end_date args are *inclusive*.
    """

    slug = 'date'
    date_field_name = 'item_date'
    _argname = 'by-date'

    _sort_value = 1.0

    def __init__(self, request, context, queryset, *args, **kwargs):
        NewsitemFilter.__init__(self, request, context, queryset, *args, **kwargs)
        args = list(args)
        schema = kwargs.get('schema') or context.get('schema')
        if schema is not None:
            if isinstance(schema, list):
                # Um. Use the first schema? This is rather arbitrary.
                schema = schema[0]
            self.label = schema.date_name
        else:
            self.label = self.slug
        gte_kwarg = '%s__gte' % self.date_field_name
        lt_kwarg = '%s__lt' % self.date_field_name
        try:
            start_date, end_date = args
            if isinstance(start_date, basestring):
                start_date = datetime.date(*map(int, start_date.split('-')))
            self.start_date = start_date
            if isinstance(end_date, basestring):
                end_date = datetime.date(*map(int, end_date.split('-')))
            self.end_date = end_date
        except (IndexError, ValueError, TypeError):
            raise FilterError("Missing or invalid date range")

        self.kwargs = {
            gte_kwarg: self.start_date,
            lt_kwarg: self.end_date+datetime.timedelta(days=1)
            }

        if self.start_date == self.end_date:
            self.value = dateformat.format(self.start_date, 'N j, Y')
        else:
            self.value = u'%s - %s' % (dateformat.format(self.start_date, 'N j, Y'), dateformat.format(self.end_date, 'N j, Y'))

        self.short_value = self.value
        self.url = '%s=%s,%s' % (self._argname,
                                 self.start_date.strftime('%Y-%m-%d'),
                                 self.end_date.strftime('%Y-%m-%d'))



    def validate(self):
        # Filtering UI does not provide a page for selecting a block.
        return {}

    def apply(self):
        """ filtering by Date """
        self.qs = self.qs.filter(**self.kwargs)


class PubDateFilter(DateFilter):

    """
    Filters on NewsItem.pub_date.
    """

    _argname = 'by-pub-date'
    date_field_name = 'pub_date'

    _sort_value = 1.0

    def __init__(self, request, context, queryset, *args, **kwargs):
        DateFilter.__init__(self, request, context, queryset, *args, **kwargs)
        self.label = 'date published'


class DuplicateFilterError(FilterError):
    """
    Raised if we try to add conflicting filters to a FilterChain.
    """
    pass

class FilterChain(SortedDict):

    """
    A set of NewsitemFilters, to be applied in a predictable order.

    The from_request() constructor can be used to create one
    based on the request URL.

    Also handles URL generation.
    """

    _base_url = ''
    schema = None

    def __repr__(self):
        return u'FilterChain(%s)' % SortedDict.__repr__(self)

    def __init__(self, data=None, request=None, context=None, queryset=None, schema=None):
        SortedDict.__init__(self, data=None)
        self.request = request
        self.context = context if context is not None else {}
        self.qs = queryset
        if data is not None:
            # We do this to force our __setitem__ to get called
            # so it will raise error on dupes.
            self.update(data)
        self.lookup_descriptions = []  # Blurbs for templates.
        self.schema = schema
        if schema:
            self.add('schema', SchemaFilter(request, context, queryset, schema=schema))
        self.other_query_params = {}

    def __setitem__(self, key, value):
        """
        stores a NewsitemFilter, and raises DuplicateFilterError if the
        key exists.
        """
        if self.has_key(key):
            raise DuplicateFilterError(key)
        SortedDict.__setitem__(self, key, value)

    def update(self, dict_):
        # Need this until http://code.djangoproject.com/ticket/15812
        # gets accepted & released.
        if getattr(dict_, 'iteritems', None) is not None:
            dict_ = dict_.iteritems()
        for k, v in dict_:
            # This works for tuples, lists, and other iterators too.
            self[k] = v

    def update_from_request(self, argstring, filter_sf_dict):
        """Update the list of filters based on the path and/or query string.

        ``argstring`` is the portion of the path that describes the
        filters (or None, in the case of "/filter/").

        ``filter_sf_dict`` is a mapping of name -> SchemaField which have
        either is_filter or is_searchable True.  We remove
        SchemaFields that we create filters for. (This is so that
        templates can display input widgets for the ones we're not
        already filtering by.)
        """
        request, context = self.request, self.context
        # TODO: can we remove some args now that we're not using
        # get_place_info_for_request?
        argstring = urllib.unquote((argstring or '').rstrip('/'))
        argstring = argstring.replace('+', ' ')
        args = []

        if argstring and argstring != 'filter':
            for arg in argstring.split(';'):
                try:
                    argname, argvalues = arg.split('=', 1)
                except ValueError:
                    raise FilterError('Invalid filter parameter %r, no equals sign' % arg)
                argname = argname.strip()
                argvalues = [v.strip() for v in argvalues.split(',')]
                if argname:
                    args.append((argname, argvalues))
        else:
            # No filters specified. Do nothing?
            pass

        qs = self.qs
        while args:
            argname, argvalues = args.pop(0)
            argvalues = [v for v in argvalues if v]
            # Date range
            if argname == 'by-date':
                self['date'] = DateFilter(request, context, qs, *argvalues, schema=self.schema)
            elif argname == 'by-pub-date':
                self['date'] = PubDateFilter(request, context, qs, *argvalues, schema=self.schema)

            # Street/address
            elif argname.startswith('streets'):
                self['location'] = BlockFilter(request, context, qs, *argvalues)
            # Location filtering
            elif argname.startswith('locations'):
                self['location'] = LocationFilter(request, context, qs, *argvalues)

            # Attribute filtering
            elif argname.startswith('by-'):
                sf_name = argname[3:]
                try:
                    sf = filter_sf_dict.pop(sf_name)
                except KeyError:
                    raise FilterError('Invalid or duplicate SchemaField name %r' % sf_name)
                self.add_by_schemafield(sf, *argvalues, _replace=True)

            else:
                raise FilterError('Invalid filter type')

        self.update_from_query_params(request)
        self.sort()
        return self

    def update_from_query_params(self, request):
        """
        Update the filters based on query parameters.

        After this is called, it's recommended to redirect
        to a normalized form of the URL, eg. self.sort(); self.make_url()

        This takes care to preserve query parameters that aren't used
        by any of the NewsitemFilters.
        """
        # Make a mutable copy so we can leave only the params that FilterChain
        # doesn't know about.
        params = request.GET.copy()
        def pop_key(key):
            # request.GET.pop() returns a sequence.
            # We only want a single value, stripped.
            val = params.pop(key, [''])[0]
            return val.strip()

        address = pop_key('address')
        if address:
            xy_radius, block_radius, cookies_to_set = block_radius_value(request)
            params.pop('radius', None)
            result = None
            try:
                result = SmartGeocoder().geocode(address)
            except AmbiguousResult, e:
                raise BadAddressException(address, block_radius, address_choices=e.choices)
            except (GeocodingException, ParsingError):
                raise BadAddressException(address, block_radius, address_choices=())

            assert result
            if result['block']:
                block = result['block']
            elif result['intersection']:
                try:
                    block = result['intersection'].blockintersection_set.all()[0].block
                except IndexError:
                    # TODO: Not sure this was deliberate, but we used to
                    # call intersection.url() here, which would
                    # raise an IndexError here if there was no
                    # matching block.  Preserving that behavior.
                    # Should this be BadAddressException?
                    raise
            else:
                # TODO: should this be BadAddressException?
                raise NotImplementedError('Reached invalid geocoding type: %r' % result)
            self.replace('location', block, block_radius)


        start_date = pop_key('start_date')
        end_date = pop_key('end_date')
        if start_date and end_date:
            try:
                start_date = parse_date(start_date, '%m/%d/%Y')
                end_date = parse_date(end_date, '%m/%d/%Y')
            except ValueError, e:
                old_e = str(e)
                del(e)
                try:
                    # Ugh, papering over wild proliferation of date formats.
                    start_date = parse_date(start_date, '%Y/%m/%d')
                    end_date = parse_date(end_date, '%Y/%m/%d')
                except ValueError, e:
                    raise BadDateException("%s; %s" % (str(e), old_e))
            if start_date.year < 1900 or end_date.year < 1900:
                # This prevents strftime from throwing a ValueError.
                raise BadDateException('Dates before 1900 are not supported.')

            self.replace('date', start_date, end_date)

        lookup_name = pop_key('textsearch')
        search_string = pop_key('q')
        if lookup_name and search_string:
            # Can raise DoesNotExist. Should that be FilterError?
            schemafield = models.SchemaField.objects.get(name=lookup_name,
                                                         schema=self.schema)
            self.replace(schemafield, search_string)

        # Stash away all query params we didn't consume.
        self.other_query_params = params

    def validate(self):
        """Check whether any of the filters were requested without
        a required value.  If so, return info about what's needed,
        as a dict.  Stops on the first one that returns anything.

        Can raise FilterError.
        """
        for key, filt in self.items():
            more_needed = filt.validate()
            if more_needed:
                return more_needed
        return {}

    def apply(self, queryset=None):
        """
        Applies each filter in the chain.
        """
        for key, filt in self._sorted_items():
            # TODO: this is an awkward way of passing the queryset.
            if queryset is not None:
                filt.qs = queryset
            filt.apply()
            queryset = filt.qs
        # Don't show any NewsItems whose Schema isn't public yet.
        # TODO: Is there a better place to do this?
        if not has_staff_cookie(self.request):
            queryset = queryset.filter(schema__is_public=True)
        return queryset

    def copy(self):
        # Overriding because default dict.copy() re-inits attributes,
        # and we want copies to be independently mutable.
        # Unfortunately this seems to require explicitly copying
        # all attributes we care about.
        clone = self.__class__()
        clone.lookup_descriptions = self.lookup_descriptions[:]
        clone._base_url = self._base_url
        clone.schema = self.schema
        clone.request = self.request
        clone.context = self.context
        clone.other_query_params = self.other_query_params
        clone.update(self)
        return clone

    def sort(self):
        """
        Put keys in optimal order.
        """
        items = self._sorted_items()
        self.clear()
        self.update(items)

    def _sorted_items(self):
        items = self.items()
        return sorted(items, key=lambda item: item[1]._sort_value)

    def replace(self, key, *values):
        """Same as self.add(), but instead of raising DuplicateFilterError
        on existing keys, replaces them.
        """
        if key in self:
            del self[key]
        return self.add(key, *values, _replace=True)


    def add(self, key, *values, **kwargs):
        """Given a string key, or a SchemaField, construct an
        appropriate NewsitemFilter with the values as arguments, and
        save it as self[key], where key is either the string key or
        derived automatically from the SchemaField.

        This does no parsing of values.

        For convenience, returns self.
        """
        # Unfortunately there's no way to accept a single optional named arg
        # at the same time as accepting arbitrary *values.
        _replace = kwargs.pop('_replace', False)
        if kwargs:
            raise TypeError("unexpected keyword args %s" % kwargs.keys())

        values = list(values)
        if isinstance(key, models.SchemaField):
            return self.add_by_schemafield(key, *values, **{'_replace': _replace})

        if not values:
            raise FilterError("no values passed for arg %s" % key)

        if isinstance(values[0], models.Location):
            val = LocationFilter(self.request, self.context, self.qs, location=values[0])
            key = val.slug
        elif isinstance(values[0], ebpub.streets.models.Block):
            block = values.pop(0)
            val = BlockFilter(self.request, self.context, self.qs, *values, block=block)
            key = val.slug
        elif isinstance(values[0], models.LocationType):
            val = LocationFilter(self.request, self.context, self.qs, *values[1:], location_type=values[0])
            key = val.slug
        elif isinstance(values[0], models.Lookup):
            val = LookupFilter(self.request, self.context, self.qs, values[0],
                               schemafield=values[0].schema_field)
        elif isinstance(values[0], (datetime.date, datetime.datetime)):
            if len(values) == 1:
                # start and end are the same date.
                values.append(values[0])
            if values[1] == 'month':
                # Whole month, regardless of precise day of first value.
                # TODO: document this!!
                _unused, end = calendar.monthrange(values[0].year, values[0].month)
                values[0] = values[0].replace(day=1)
                values[1] = values[0].replace(day=end)
            if key == 'pubdate':
                key = 'date'
                val = PubDateFilter(self.request, self.context, self.qs, *values, schema=self.schema)
            else:
                val = DateFilter(self.request, self.context, self.qs, *values, schema=self.schema)
        elif isinstance(values[0], models.Schema) or (isinstance(values[0], list) and values[0] and isinstance(values[0][0], models.Schema)):
            key = 'schema'
            schema = values[0]
            val = SchemaFilter(self.request, self.context, self.qs, *values, schema=schema)
            self.schema = schema
            for filt in self.values():
                # TODO: this may be too late if some things depend on
                # schema during __init__()
                filt.schema = schema
        else:
            val = values[0]
            # We seem to get some unexpected types here sometimes:
            # dicts, strings...
            if not isinstance(val, NewsitemFilter):
                logger.warn("SchemaFilter.add called with key %r and unexpected values %r, not adding."
                            % (key, values))
                logger.warn('path was: %s' % self.request.get_full_path())
                return self

        if _replace and key in self:
            del self[key]
        self[key] = val
        return self

    def add_by_schemafield(self, schemafield, *values, **kwargs):
        """Given a SchemaField, construct an appropriate
        NewsitemFilter with the values as arguments, and save it as
        self[schemafield.name].

        For convenience, returns self.
        """
        # Unfortunately there's no way to accept a single optional named arg
        # at the same time as accepting arbitrary *values.
        _replace = kwargs.pop('_replace', False)
        if kwargs:
            raise TypeError("unexpected keyword args %s" % kwargs.keys())

        values = list(values)
        key = schemafield.name
        if schemafield.is_lookup:
            filterclass = LookupFilter
        elif schemafield.is_type('bool'):
            filterclass = BoolFilter
        elif schemafield.is_searchable:
            filterclass = TextSearchFilter
        else:
            # Ints, varchars, dates, times, and datetimes.
            filterclass = AttributeFilter

        if _replace and key in self:
            del self[key]

        self[key] = filterclass(self.request, self.context, self.qs, schemafield=schemafield, *values)

        if schemafield.is_lookup and getattr(self[key], 'look', None) is not None:
            self.lookup_descriptions.append(self[key].look)

        return self


    def make_breadcrumbs(self, additions=(), removals=(), stop_at=None, 
                         base_url=None):
        """
        Returns a list of (label, URL) pairs suitable for making
        breadcrumbs for the schema_filter view.

        If ``base_url`` is passed, URLs generated will be include that
        that; otherwise fall back to self.base_url, which falls
        back to self.schema.url().

        If ``stop_at`` is passed, the key specified will be the last
        one used for the breadcrumb list.

        If ``removals`` is passed, the specified filter keys will be
        excluded from the breadcrumb list.

        If ``additions`` is passed, the specified (key, NewsitemFilter)
        pairs will be added to the end of the breadcrumb list.

        (In some cases, you can pass (key, [args]) and it will figure
        out what kind of NewsitemFilter to create.  TODO: document
        this!!)

        Also, if self.other_query_params is a dictionary, its items
        will be added as query parameters to all the URLs.  This can
        be used to add or preserve query parameters that aren't
        relevant to the FilterChain.

        """
        # TODO: Can filter_reverse leverage this? Or vice-versa?
        clone = self.copy()
        for key in removals:
            try:
                del clone[key]
            except KeyError:
                logger.warn("can't delete nonexistent key %s" % key)

        for key, values in additions:
            clone.replace(key, *values)

        base_url = base_url or clone.base_url

        crumbs = []
        filter_params = []
        other_query_params = urllib.urlencode(sorted(self.other_query_params.items()),
                                              doseq=True)
        for key, filt in clone._items_with_labels():
            # I'm not sure why we prefer short_value to label, but that's what
            # the old code did.
            label = getattr(filt, 'short_value', None) or getattr(filt, 'value', None) or getattr(filt, 'label', None)
            assert label is not None
            label = label.title()
            if label and getattr(filt, 'url', None) is not None:
                filter_params.append(filt.url)
                url = '%s%s/' % (base_url, ';'.join(filter_params))
                if other_query_params:
                    url = '%s?%s' % (url, other_query_params)
                crumbs.append((label, url))
            if key == stop_at:
                break
        return crumbs

    def make_urls(self, additions=(), removals=(), stop_at=None, base_url=None):
        """
        Just like ``make_breadcrumbs`` but only URLs are included in
        the output.
        """
        crumbs = self.make_breadcrumbs(additions, removals, stop_at, base_url)
        return [crumb[1] for crumb in crumbs]

    def make_url(self, additions=(), removals=(), stop_at=None, base_url=None):
        """
        Makes one URL representing all the filters of this filter chain,
        for the schema_filter view.
        """
        crumbs = self.make_breadcrumbs(additions, removals, stop_at, base_url)
        if crumbs:
            return crumbs[-1][1]
        else:
            return base_url or self.base_url

    def add_by_place_id(self, pid):
        """
        ``pid`` is a place id string as used by parse_pid and make_pid,
        identifying a location or block (and if a block, a radius).
        """
        place, block_radius, xy_radius = parse_pid(pid)
        if isinstance(place, models.Block):
            self['location'] = BlockFilter(self.request, self.context, self.qs,
                                           block_radius, block=place)
        else:
            self['location'] = LocationFilter(self.request, self.context, self.qs,
                                              location=place)

    def filters_for_display(self):
        """
        If a filter has no label, that means don't show it in various
        places in the UI.  This is a convenience to get only the
        values that should be shown.
        """
        return [v for (k, v) in self._items_with_labels()]

    def _items_with_labels(self):
        return [(k, v) for (k, v) in self.items() if getattr(v, 'label', None)]

    def _get_base_url(self):
        return self._base_url or self.schema.url() + 'filter/'
    def _set_base_url(self, url):
        self._base_url = url
    base_url = property(_get_base_url, _set_base_url)


class BadAddressException(Exception):
    def __init__(self, address, block_radius, address_choices, message=None):
        self.address = address
        self.block_radius = block_radius
        self.address_choices = address_choices
        self.message = message
        self.radius_slug = radius_slug(block_radius)


class BadDateException(Exception):
    pass


# Block radius utility functions.
# Moved here because nothing else was using them.

def radius_slug(radius):
    """Return radius string like 8-blocks, 1-block ..."""
    radius = unicode(radius)
    return u'%s-block%s' % (radius, radius != '1' and 's' or '')

def radius_from_slug(slug):
    """Extract radius from a string like 8-blocks, 1-block, ..."""
    slug = unicode(slug)
    radius = slug.split('-')[0]
    assert radius.isdigit()
    return radius

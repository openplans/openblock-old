"""
Use cases:

  1. Generate a chain of filters, given view arguments and/or query
     string.

  2. Generate reverse urls, complete with query string (if we use them),
     given one or more filters.

     a. For schema_filter() html view

     b. For REST API view


Chain of filters needs to support:

  1. Add a filter to the chain, by name.

  2. Remove a filter from the chain, by name

  3. get a filter from the chain, by name

  4. raise Http404() if conflicting filters are added (eg. two date
     filters) - or raise a custom exception which wrapper views can
     handle however they like.

  5. OPTIMIZATION: normalize the order of filters by
     increasing expense

     ... which I guess to be something like: schema, date, non-lookup
     attrs, block/location, lookup attrs, text search. This would need
     profiling with lots of test data.

  6. SEO and CACHEABILITY: Redirect to a normalized form of the URL
     for better cacheability.

     ... handle this in external code


  7. copy() a filter chain - useful for making mutated variations,
     which could be used with our reverse() to create "remove
     this filter" links in the UI.

  8. get a list of breadcrumb links for the whole chain.

     it's still debatable whether breadcrumbs make sense here at all.

     if they do, this would replace
     templatetags.eb_filter.filter_breadcrumb_link() which by
     comparison takes too many params and is called N times.

     this could be done by external code: it's not really
     core to filtering and is irrelevant in eg. the REST API views.


Currently, each 'filter' *as seen by templates* is a dict with keys like:

  {'name': 'date',
   'label': schema.date_name,
   'short_value': ...,
   'value': dateformat.format(start_date, 'N j, Y'),
   'url':  XXX fragment of url path, like '/filter/arg1/arg2/' in the original version or '/filter=arg1,arg2/' in my alternate version.
   'location_name': XXX string, only used when name='location',
   'location_object': XXX a Block or Location,
   }

... but since django templates don't distinguish between attrs and
items, there's no reason a filter couldn't be an object with those
attributes/properties too.  And some of that may only be needed by the
breadcrumb template tag, which should go away (see above).

---------------------------------------------------

Things that can happen in current schema_filter() view when a filter
gets "applied":

  * an existing queryset might get modified in various ways:
     qs = qs.filter(**kwargs)  # date
     qs = qs.by_attribute(schemafield, lookup.id)  # Lookup
     qs = qs.by_attribute(schemafield, True|False|None)  # Boolean Lookup
     qs = qs.text_search(schemafield, query)  # Text search Lookup

  * might redirect to a better view (eg. adding a default block radius)

     ... this isn't really the responsibility of the filter,
     maybe could be handled as part of url normalization

  * if there are no args to this filter, and it requires some,
    immediately *return* (not redirect) filter_lookup_list.html with a list of
    possible values ('lookup_list')

    ... maybe could handle this in external code, just after url
    normalization?  not sure since the specific filter may need to be
    intimately aware of what needs to happen here.

    example: http://demo.openblockproject.org/local-news/locations/zipcodes/ allows you to select a zip code

  * template context may have some new stuff added.

  * a callback might get called (mainly context.update(get_place_info_for_request()), used when filtering by block or location.
    ... this might also mutate the queryset, in context['newsitem_qs']


  * 404 if filter type is invalid.


"""


#from django.http import Http404
from django.http import HttpResponseRedirect
from ebpub.db import constants
from ebpub.db import models
from ebpub.db.utils import get_place_info_for_request
import datetime
import re
from django.utils import dateformat

# STRAW MAN DESIGN FOLLOWS

# In ebpub.db.views, example usage would look like:
def schema_filter(request, *args, **kw):
    filterchain = FilterChain(request, *args, **kw)
    normalized_url = normalize_url_with_filters(request, filterchain)
    if normalized_url != request.get_full_path():
        return HttpResponseRedirect(normalized_url)

    context = {}
    qs = NewsItem.objects.all()
    for sfilter in filterchain:
        info_needed = filterchain.more_info_needed()
        if info_needed:
            context.update(info_needed)
            return eb_render(request, 'db/filter_lookup_list.html', context)
        qs = sfilter.apply(qs)

    # ... now post-filtering stuff, currently starting at:
    LOOKUP_MIN_DISPLAYED = 7
    # ... etc.
    return eb_render(request, 'db/filter.html', context)



class SchemaFilter(object):
    def __init__(self, request, context, queryset=None, *args, **kw):
        self.qs = queryset
        self.context = context
        self.request = request

    def apply(self):
        """mutate the queryset, and any other state that needs sharing
        with others.
        """
        raise NotImplementedError

    def more_info_needed(self):
        """
        If we didn't get enough info from the args, eg. it's a
        Location filter but no location was specified, then return a
        dict of stuff for putting in a template context.
        ... or maybe something more generic across both REST and UI views
        """
        return None

    def get(self, key, default=None):
        # Emulate a dict to make legacy code in ebpub.db.breadcrumbs happy
        return getattr(self, key, default)

    def __getitem__(self, key):
        # Emulate a dict to make legacy code in ebpub.db.breadcrumbs happy
        default = object()
        result = getattr(self, key, default)
        if result is default:
            raise KeyError(key)
        return result


class FilterError(Exception):
    def __init__(self, msg, url=None):
        self.msg = msg
        self.url = url

    def __str__(self):
        return repr(self.msg)

class AttributeFilter(SchemaFilter):

    def __init__(self, request, context, queryset, *args, **kwargs):
        SchemaFilter.__init__(self, request, context, queryset, *args, **kwargs)
        self.schemafield = kwargs['schemafield']
        self.name = self.schemafield.name
        self.argname = 'by-%s' % self.schemafield.name
        self.url = None
        self.value = self.short_value = ''
        self.label = self.schemafield.pretty_name


class TextSearchFilter(AttributeFilter):
    def __init__(self, request, context, queryset, *args, **kwargs):
        AttributeFilter.__init__(self, request, context, queryset, *args, **kwargs)
        self.label = self.schemafield.pretty_name
        if not args:
            raise FilterError('Text search lookup requires search params')
        self.query = ', '.join(args)
        self.short_value = self.query
        self.value = self.query
        self.url = 'by-%s=%s' % (self.schemafield.slug, self.query)

    def apply(self):
        self.qs = self.qs.text_search(self.schemafield, self.query)

    def more_info_needed(self):
        return {}

class BoolFilter(AttributeFilter):

    def __init__(self, request, context, queryset, *args, **kwargs):
        AttributeFilter.__init__(self, request, context, queryset, *args, **kwargs)
        self.label = None
        if len(args) > 1:
            raise FilterError("Invalid boolean arg %r" % ','.join(args))
        elif len(args) == 1:
            self.boolslug = args[0]
            try:
                self.real_val = {'yes': True, 'no': False, 'na': None}[self.boolslug]
            except KeyError:
                raise FilterError('Invalid boolean value %r' % self.boolslug)
            self._got_args = True
        else:
            # No args.
            self.value = u'By whether they %s' % self.schemafield.pretty_name_plural
            self._got_args = False

    def more_info_needed(self):
        if self._got_args:
            return {}
        return {
            'filter_argname': self.argname,
            'lookup_type': self.value[3:],
            'lookup_type_slug': self.schemafield.slug,
            'lookup_list': [{'slug': 'yes', 'name': 'Yes'}, {'slug': 'no', 'name': 'No'}, {'slug': 'na', 'name': 'N/A'}],
            }


    def apply(self):
        self.qs = self.qs.by_attribute(self.schemafield, self.real_val)
        self.label = self.schemafield.pretty_name
        self.short_value = {True: 'Yes', False: 'No', None: 'N/A'}[self.real_val]
        self.value = u'%s%s: %s' % (self.label[0].upper(), self.label[1:], self.short_value)
        self.url = 'by-%s=%s' % (self.schemafield.slug, self.boolslug)


class LookupFilter(AttributeFilter):

    def __init__(self, request, context, queryset, *args, **kwargs):
        AttributeFilter.__init__(self, request, context, queryset, *args, **kwargs)
        try:
            slug = args[0]
            self._got_args = True
        except IndexError:
            self._got_args = False
        if self._got_args:
            try:
                self.look = models.Lookup.objects.get(
                    schema_field__id=self.schemafield.id, slug=slug)
            except models.Lookup.DoesNotExist:
                raise FilterError("No such lookup %r" % slug)
            self.value = self.look.name
            self.short_value = self.value
            self.url = 'by-%s=%s' % (self.schemafield.slug, slug)

    def more_info_needed(self):
        if self._got_args:
            return {}
        lookup_list = models.Lookup.objects.filter(schema_field__id=self.schemafield.id).order_by('name')
        return {
            'lookup_type': self.schemafield.pretty_name,
            'lookup_type_slug': self.schemafield.slug,
            'filter_argname': self.argname,
            'lookup_list': lookup_list,
        }

    def apply(self):
        self.qs = self.qs.by_attribute(self.schemafield, self.look.id)


class LocationFilter(SchemaFilter):

    name = 'location'  # XXX deprecate this? used by eb_filter template tag
    argname = 'locations'

    def __init__(self, request, context, queryset, *args, **kwargs):
        SchemaFilter.__init__(self, request, context, queryset, *args, **kwargs)
        if not args:
            raise FilterError("not enough args")
        self.location_type_slug = args[0]
        try:
            self.loc_name = args[1]
            self._got_args = True
        except IndexError:
            self._got_args = False

    def more_info_needed(self):
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
                'filter_argname': self.argname,
                }


    def apply(self):
        """
        filtering by Location
        """
        self.context.update(get_place_info_for_request(
                self.request, self.location_type_slug, self.loc_name,
                place_type='location', newsitem_qs=self.qs))
        loc = self.context['place']
        #loc = url_to_location(location_type_slug, argvalues.pop())
        #qs = qs.filter(newsitemlocation__location__id=loc.id)
        #qs = qs.filter(location__bboverlaps=loc.location.envelope)
        self.qs = self.context['newsitem_qs']
        self.label = loc.location_type.name
        self.short_value = loc.name
        self.value = loc.name
        self.url = 'locations=%s,%s' % (self.location_type_slug, loc.slug)
        self.location_name = loc.name
        self.location_object = loc

from ebpub.metros.allmetros import get_metro


class BlockFilter(SchemaFilter):

    name = 'location'

    def __init__(self, request, context, queryset, *args, **kwargs):
        SchemaFilter.__init__(self, request, context, queryset, *args, **kwargs)
        args = list(args)
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
            self.block_radius = args.pop(0)
        except IndexError:
            from ebpub.db.views import block_radius_value
            xy_radius, block_radius, cookies_to_set = block_radius_value(request)
            from ebpub.db.views import radius_url
            raise FilterError('missing radius', url=radius_url(request.path, block_radius))
        m = re.search('^%s$' % constants.BLOCK_URL_REGEX, self.block_range)
        if not m:
            raise FilterError('Invalid block URL: %r' % self.block_range)
        self.url_to_block_args = m.groups()


    def more_info_needed(self):
        # Filtering UI does not provide a page for selecting a block.
        return {}

    def apply(self):
        """ filtering by Block """

        self.context.update(get_place_info_for_request(
                self.request, self.city_slug, self.street_slug,
                *self.url_to_block_args,
                place_type='block', newsitem_qs=self.qs))

        block = self.context['place']
        value = '%s block%s around %s' % (self.block_radius, (self.block_radius != '1' and 's' or ''), block.pretty_name)

        self.label = 'Area'
        self.short_value = value
        self.value = value
        from ebpub.db.views import radius_urlfragment
        self.url = 'streets=%s,%s,%s' % (block.street_slug,
                                         '%d-%d' % (block.from_num, block.to_num), 
                                         radius_urlfragment(self.block_radius))
        self.location_name = block.pretty_name
        self.location_object = block

class DateFilter(SchemaFilter):

    name = 'date'
    date_field_name = 'item_date'
    argname = 'by-date'  # XXX this doesn't feel like it belongs here.

    def __init__(self, request, context, queryset, *args, **kwargs):
        SchemaFilter.__init__(self, request, context, queryset, *args, **kwargs)
        args = list(args)
        self.label = context['schema'].date_name
        gte_kwarg = '%s__gte' % self.date_field_name
        lt_kwarg = '%s__lt' % self.date_field_name
        try:
            start_date, end_date = args
            self.start_date = datetime.date(*map(int, start_date.split('-')))
            self.end_date = datetime.date(*map(int, end_date.split('-')))
        except (IndexError, ValueError, TypeError):
            raise FilterError("Missing or invalid date range")

        self.kwargs = {
            gte_kwarg: self.start_date,
            lt_kwarg: self.end_date+datetime.timedelta(days=1)
            }

    def more_info_needed(self):
        # Filtering UI does not provide a page for selecting a block.
        return {}

    def apply(self):
        """ filtering by Date """
        self.qs = self.qs.filter(**self.kwargs)
        if self.start_date == self.end_date:
            value = dateformat.format(self.start_date, 'N j, Y')
        else:
            value = u'%s \u2013 %s' % (dateformat.format(self.start_date, 'N j, Y'), dateformat.format(self.end_date, 'N j, Y'))


        self.value = value
        self.short_value = value
        self.url = '%s=%s,%s' % (self.argname,
                                 self.start_date.strftime('%Y-%m-%d'), 
                                 self.end_date.strftime('%Y-%m-%d'))


class PubDateFilter(DateFilter):

    argname = 'by-pub-date'
    date_field_name = 'pub_date'

    def __init__(self, request, context, queryset, *args, **kwargs):
        DateFilter.__init__(self, request, context, queryset, *args, **kwargs)
        self.label = 'date published'


class DuplicateFilterError(FilterError):
    pass

from django.utils.datastructures import SortedDict
class SchemaFilterChain(SortedDict):

    def __setitem__(self, key, value):
        """
        stores a SchemaFilter.
        """
        if self.has_key(key):
            raise DuplicateFilterError(key)
        SortedDict.__setitem__(self, key, value)

    def normalized_clone(self):
        """
        Return a copy of self with keys in optimal order.
        """
        items = self._normalize_order_of_items(self.items())
        return SchemaFilterChain(items)

    def _normalize_order_of_items(self, items):
        raise NotImplementedError

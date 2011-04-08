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


from django.http import Http404
from ebpub.db import models
from ebpub.db.views import get_place_info_for_request

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
    pass

class LocationFilter(SchemaFilter):

    name = 'location'

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
                # XXX 'filter_argname': argname,
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



class BlockFilter(LocationFilter):
    def apply(self):
        """ filtering by Block """

from django.utils.datastructures import SortedDict
class SchemaFilterChain(SortedDict):

    def __setitem__(self, key, value):
        """
        stores a SchemaFilter.
        """
        if isinstance(value, LocationFilter) and self.has_location_filter:
            raise DuplicateFilter()
        # etc.

    def normalized_clone(self):
        """
        Return a copy of self with keys in optimal order.
        """
        items = self._normalize_order_of_items(self.items())
        return SchemaFilterChain(items)

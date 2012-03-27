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

"""
Template tags for working with
:py:class:`NewsItem <ebpub.db.models.NewsItem>`,
:py:class:`Location <ebpub.db.models.Location>`,
etc.

To use these, your template must include:

.. code-block:: html+django

    {% load eb %}

"""
from django import template
from django.core.cache import cache
from django.template.defaultfilters import stringfilter
from django.template.loader import select_template
from ebpub.db.models import LocationType
from ebpub.db.models import Lookup
from ebpub.db.models import NewsItem
from ebpub.db.models import SchemaField, Schema
from ebpub.db.schemafilters import FilterChain
from ebpub.db.utils import populate_attributes_if_needed
from ebpub.metros import allmetros
from ebpub.utils.bunch import bunch, bunchlong, stride
from ebpub.utils.dates import today
from ebpub.utils.models import is_instance_of_model
from ebpub.utils.text import smart_title

import json
import re

register = template.Library()

# Split a list into sub-lists in various ways; See ebpub.utils.bunch.
register.filter('bunch', bunch)
register.filter('bunchlong', bunchlong)
register.filter('stride', stride)

def METRO_NAME():
    """Prints the metro_name from get_metro(), titlecase.

    Example:

    .. code-block:: html+django

       <h1>{% METRO_NAME %}</h1>

    """
    name = allmetros.get_metro()['metro_name']
    if name[0] != name[0].upper:
        name = name.title()
    return name
register.simple_tag(METRO_NAME)

def isdigit(value):
    """Filter that returns whether the value is a digit.

    Example:

    .. code-block:: html+django

      {% if "123"|isdigit %} It's a digit {% endif %}
      {% if not "Fred"|isdigit %} It's not a digit {% endif %}


    Python examples:

    .. code-block:: python

    >>> isdigit("1")
    True
    >>> isdigit("999")
    True
    >>> isdigit("42.1")
    False
    >>> isdigit("hello")
    False
    >>> isdigit("")
    False

    """
    return value.isdigit()
register.filter('isdigit', stringfilter(isdigit))


def lessthan(value, arg):
    """Filter. Obsolete since Django 1.1:  Use the < operator instead.
    """
    return int(value) < int(arg)   # pragma: no cover
register.filter('lessthan', lessthan)

def greaterthan(value, arg):
    """Filter. Obsolete since Django 1.1:  Use the > operator instead.
    """
    return int(value) > int(arg)  # pragma: no cover
register.filter('greaterthan', greaterthan)

def schema_plural_name(schema, value):
    """
    Tag that shows singular or plural name of a schema, depending on
    ``value``.  Example:

    .. code-block:: html+django

        {% schema_plural_name schema 3 %}  --> Restaurant Inspections
        {% schema_plural_name schema 1 %}  --> Restaurant Inspection

    """
    if isinstance(value, (list, tuple)):
        value = len(value)
    return (value == 1) and schema.name or schema.plural_name
register.simple_tag(schema_plural_name)

def safe_id_sort(value, arg):
    """
    Filter that sorts like Django's built-in "dictsort", but sorts
    second by the ID attribute, to ensure sorts always end up the
    same.

    Example:

    .. code-block:: html+django

      {% for item in itemlist|safe_id_sort "item_date" %} ... {% endfor %}

    """
    var_resolve = template.Variable(arg).resolve
    decorated = [(var_resolve(item), item.id, item) for item in value]
    decorated.sort()
    return [item[2] for item in decorated]
safe_id_sort.is_safe = False
register.filter('safe_id_sort', safe_id_sort)


@register.simple_tag(takes_context=True)
def get_metro_list(context):
    """
    Tag that puts settings.METRO_LIST into the context as METRO_LIST.

    Example:

    .. code-block:: html+django

      {% get_metro_list %}
      {% for metro in METRO_LIST %}
        <p>The metro is {{ metro.city_name }}</p>
      {% endfor %}
    """
    context['METRO_LIST'] = allmetros.METRO_LIST
    return ''


@register.simple_tag(takes_context=True)
def get_metro(context):
    """
    Tag that puts get_metro() into the context as METRO

    Example:

    .. code-block:: html+django

      {% get_metro %}
      <p>Current metro is {{ METRO.city_name }}</p>

    """
    context['METRO'] = allmetros.get_metro()
    return u''


class GetNewsItemNode(template.Node):
    def __init__(self, newsitem_variable, context_var):
        self.variable = template.Variable(newsitem_variable)
        self.context_var = context_var

    def render(self, context):
        newsitem_id = self.variable.resolve(context)
        try:
            context[self.context_var] = NewsItem.objects.select_related().get(id=newsitem_id)
        except NewsItem.DoesNotExist:
            pass
        return ''

def get_newsitem(parser, token):
    """
    Tag that puts a newsitem with the given ID in the context with the given
    variable name. Examples:

    .. code-block:: html+django

      {% get_newsitem some_id as my_item %}
      {% get_newsitem '23' as my_other_item %}
      <p>{{ my_item.title }}</p>
      <p>{{ my_other_item.title }}</p>

    """
    bits = token.split_contents()
    if len(bits) != 4:
        raise template.TemplateSyntaxError('%r tag requires 3 arguments' % bits[0])
    return GetNewsItemNode(bits[1], bits[3])
register.tag('get_newsitem', get_newsitem)

## This is a very obscure feature that we don't use anywhere...
# class GetNewerNewsItemNode(template.Node):
#     def __init__(self, newsitem_variable, newsitem_list_variable, context_var):
#         self.newsitem_var = template.Variable(newsitem_variable)
#         self.newsitem_list_var = template.Variable(newsitem_list_variable)
#         self.context_var = context_var

#     def render(self, context):
#         newsitem = self.newsitem_var.resolve(context)
#         newsitem_list = self.newsitem_list_var.resolve(context)
#         if newsitem_list and newsitem_list[0].item_date > newsitem.item_date:
#             context[self.context_var] = newsitem_list[0]
#         else:
#             context[self.context_var] = None
#         return ''
#
# def get_newer_newsitem(parser, token):
#     """Tag which, given a newsitem, and a list of other newsitems,
#     puts only those items more recent than the first item into a new
#     context variable.

#     Example::

#       {% get_more_recent_newsitem [newsitem] [item_list] as [context_var] %}
#     """
#     bits = token.split_contents()
#     if len(bits) != 5:
#         raise template.TemplateSyntaxError('%r tag requires 4 arguments' % bits[0])
#     return GetNewerNewsItemNode(bits[1], bits[2], bits[4])
# register.tag('get_newer_newsitem', get_newer_newsitem)

class GetNewsItemListByAttributeNode(template.Node):
    def __init__(self, schema_id_variable, newsitem_id_variable, att_name, att_value_variable, context_var):
        self.schema_id_variable = template.Variable(schema_id_variable)
        if newsitem_id_variable is None:
            self.newsitem_id_variable = None
        else:
            self.newsitem_id_variable = template.Variable(newsitem_id_variable)
        self.att_name = att_name
        self.att_value_variable = template.Variable(att_value_variable)
        self.context_var = context_var

    def render(self, context):
        schema_id = self.schema_id_variable.resolve(context)
        if hasattr(schema_id, 'id'):
            # It could be a Schema.
            schema_kwargs = {'schema__id': schema_id.id}
        elif isinstance(schema_id, basestring):
            # It could be a slug.
            schema_kwargs = {'schema__slug': schema_id}
        else:
            schema_kwargs = {'schema__id': schema_id}

        att_value = self.att_value_variable.resolve(context)
        sf = SchemaField.objects.select_related().get(name=self.att_name, **schema_kwargs)
        queryset = NewsItem.objects.select_related().filter(**schema_kwargs)

        if self.newsitem_id_variable is not None:
            newsitem_id = self.newsitem_id_variable.resolve(context)
            if hasattr(newsitem_id, 'id'):
                # It could be a NewsItem.
                newsitem_id = newsitem_id.id
            queryset = queryset.exclude(id=newsitem_id)

        queryset = queryset.by_attribute(sf, att_value).order_by('-item_date')
        populate_attributes_if_needed(queryset, [sf.schema])

        # We're assigning directly to context.dicts[-1] so that the variable
        # gets set in the top-most context in the context stack. If we didn't
        # do this, the variable would only be available within the specific
        # {% block %} from which the template tag was called, because the
        # {% block %} implementation does a context.push() and context.pop().
        context.dicts[-1][self.context_var] = queryset

        return ''

def get_newsitem_list_by_attribute(parser, token):
    """
    Tag that gets a list of NewsItems with a given attribute value,
    and saves it in a context variable.
    Optionally exclude a NewsItem by id.  (Useful if you have a NewsItem
    and you want to build a list of similar NewsItems without 
    including the one you already have.)

    Syntax:

    .. code-block:: html+django

      {% get_newsitem_list_by_attribute [schema] [newsitem_to_ignore] [att_name]=[value_or_var_containing_value] as [context_var] %}
      {% get_newsitem_list_by_attribute [schema] [att_name]=[value_or_var_containing_value] as [context_var] %}

    The ``schema`` and ``newsitem_to_ignore`` arguments can be either
    IDs or instances of Schema and NewsItem, respectively.
    ``Schema`` can also be specified by slug.

    Example 1. Here's a list of the latest 3 items that have the "tag" value of
    "garage sale" and schema slug "local-news":

    .. code-block:: html+django

      {% get_newsitem_list_by_attribute "local-news" tag="garage sale" as recent_sales %}
      {% for sale in recent_sales|slice:":3" %}
         <li><i>{{ sale.title }}</i></li>
      {% endfor %}

    Example 2. Here's a list of items that have the same "business_id" value as
    ``item`` does.   ``item`` itself is excluded from the list.

    .. code-block:: html+django

      {% get_newsitem_list_by_attribute item.schema item business_id=item.attributes.business_id as other_licenses %}
      {% for item in other_licenses %}
         <li><i>{{ item.title }}</i>
      {% endfor %}


    """
    bits = token.split_contents()
    if len(bits) == 5:
        att_arg_index = 2
        news_item_var=None
    elif len(bits) == 6:
        att_arg_index = 3
        news_item_var = bits[2]
    else:
        raise template.TemplateSyntaxError('%r tag requires 4 or 5 arguments' % bits[0])
    if bits[att_arg_index].count('=') != 1:
        raise template.TemplateSyntaxError('%r tag argument must contain 1 equal sign' % bits[0])
    att_name, att_value_variable = bits[att_arg_index].split('=')
    return GetNewsItemListByAttributeNode(bits[1], news_item_var, att_name, att_value_variable, bits[-1])

register.tag('get_newsitem_list_by_attribute', get_newsitem_list_by_attribute)


class NewsItemListBySchemaNode(template.Node):
    def __init__(self, newsitem_list_variable, is_ungrouped):
        self.variable = template.Variable(newsitem_list_variable)
        self.is_ungrouped = is_ungrouped

    def render(self, context):
        ni_list = self.variable.resolve(context)

        # For convenience, the newsitem_list might just be a single newsitem,
        # in which case we turn it into a list.
        if isinstance(ni_list, NewsItem):
            ni_list = [ni_list]

        schema = ni_list[0].schema
        template_list = ['db/snippets/newsitem_list/%s.html' % schema.slug,
                         'db/snippets/newsitem_list.html']
        schema_template = select_template(template_list)
        return schema_template.render(template.Context({
            'is_grouped': not self.is_ungrouped,
            'schema': schema,
            'newsitem_list': ni_list,
            'num_newsitems': len(ni_list),
            'place': context.get('place'),
            'is_block': context.get('is_block'),
            'block_radius': context.get('block_radius'),
            'today': today,
        }))


def newsitem_list_by_schema(parser, token):
    """
    Tag that renders a NewsItem, or list of NewsItems, using the
    appropriate newsitem_list template, optionally grouped by schema.

    Syntax:

    .. code-block:: html+django


      {% newsitem_list_by_schema [newsitem_or_newsitem_list] [ungrouped?] %}


    Examples:

    .. code-block:: html+django

      {% newsitem_list_by_schema newsitem "ungrouped" %}
      {% newsitem_list_by_schema newsitem_list %}

    """
    bits = token.split_contents()
    if len(bits) not in (2, 3):
        raise template.TemplateSyntaxError('%r tag requires one or two arguments' % bits[0])
    if len(bits) == 3:
        if bits[2] != 'ungrouped':
            raise template.TemplateSyntaxError('Optional last argument to %r tag must be the string "ungrouped"' % bits[0])
        is_ungrouped = True
    else:
        is_ungrouped = False
    return NewsItemListBySchemaNode(bits[1], is_ungrouped)
register.tag('newsitem_list_by_schema', newsitem_list_by_schema)


def contains(value, arg):
    """Filter to check whether ``arg`` is in ``value``.
    Obsolete since Django 1.2, use the 'in' operator instead.

    Example:

    .. code-block:: html+django

      {% if "Bob" in name_list %}
         Hi Bob!
      {% endif %}
    """
    return arg in value  # pragma: no cover
register.filter('contains', contains)


class SearchPlaceholderNode(template.Node):

    #See search_placeholder()

    def __init__(self, prefix, var_name):
        self.prefix = prefix.strip()
        self.var_name = var_name.strip()

    def render(self, context):
        cachekey = 'SearchPlaceholderNode'
        result = cache.get(cachekey)
        if result is None:
            from ebpub.db.models import LocationType
            types = LocationType.objects.filter(is_significant=True)
            types = list(types.order_by('name').values('name'))
            names = ['address'] + [loctype['name'].lower() for loctype in types]
            if len(names) > 3:
                # like "foo, bar, baz, ..."
                result = u'%s, ...' % (u', '.join(names[:3]))
            elif len(names) > 2:
                # like "foo, bar, or baz"
                result = u'%s, or %s' % (u', '.join(names[:-1]), names[-1])
            elif len(names) == 2:
                # like "foo or bar"
                result = u'%s or %s' % tuple(names)
            else:
                result = names[0]
            cache.set(cachekey, result, 60 * 60)
        if self.prefix:
            result = u'%s %s' % (self.prefix, result)
        else:
            # By default we want just the 1st letter forced caps,
            # and only when there's no prefix.
            result = result[0].upper() + result[1:]
        context[self.var_name] = result
        return ''

def search_placeholder(parser, token):
    """
    Tag that stores in a context variable a list of
    :py:class:`ebpub.db.models.LocationType`,
    plus 'address', with an optional prefix.

    Useful for search form widgets where we want to use this as
    placeholder text on the input, and need to write exactly the same string
    over and over because javascript will be checking for the
    placeholder text, restoring it, etc.

    Example:

    .. code-block:: html+django

      {% set_search_placeholder "Some prefix" as some_var %}
      <p>{{ some_var }}</p>

    If you have LocationTypes named 'ZIP' and 'neighborhood,'
    this would output in the template:

    .. code-block:: html+django

      <p>Some prefix address, ZIP, or neighborhood</p>
    """
    # In Django 1.4, this could become an assignment_tag as per
    # https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#howto-custom-template-tags-assignment-tags
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    prefix, var_name = m.groups()
    if not (prefix[0] == prefix[-1] and prefix[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return SearchPlaceholderNode(prefix[1:-1], var_name)

register.tag('set_search_placeholder', search_placeholder)


@register.simple_tag(takes_context="true")
def featured_lookup_for_item(context, newsitem, attribute_key):
    """Tag that, given a NewsItem, finds any :ref:`featured_lookups`
    that correspond to its values for the named attribute.
    Saves them in the current context under the same name as the attribute.

    Example:

    .. code-block:: html+django

      {% featured_lookup_for_item item 'tags' %}
      {% for tag in tags %}
        This item has tag {{ tag }}
      {% endfor %}

    """
    lookups = Lookup.objects.featured_lookups_for(newsitem, attribute_key)
    context[attribute_key] = lookups
    return ""


@register.simple_tag(takes_context="true")
def get_featured_lookups_by_schema(context):
    """
    Get all :ref:`featured_lookups` names and URLs for them; 
    puts in the context as
    'featured_lookups', a mapping grouped by schema.

    Example:

    .. code-block:: html+django

        {% get_featured_lookups_by_schema %}
        {% for schema, lookups in featured_lookups.items %}
           <ul>{{ schema }}
            {% for info in lookups %}
              <a href="{{ info.url }}">{{ info.lookup }}</a>
               ...
            {% endfor %}
        {% endfor %}
    """
    lookups = {}
    for lookup in Lookup.objects.filter(featured=True).select_related():
        sf = lookup.schema_field
        schema = sf.schema
        filters = FilterChain(schema=schema)
        filters.add(sf, lookup)
        info = {'lookup': lookup.name, 'url': filters.make_url()}
        lookups.setdefault(schema.slug, []).append(info)
    context['featured_lookups'] = lookups
    return u''


@register.simple_tag()
def json_lookup_values_for_attribute(schema_slug, sf_name):
    """Given a schema slug and attribute name, returns
    all the current Lookup values of the relevant attribute,
    as a JSON-formatted list.

    Assumes the relevant schemafield has is_lookup=True.

    Example:

    .. code-block:: html+django

     <script>
      var lookups = {% json_lookup_values_for_attribute 'police-reports' 'violations' %};
     </script>

    Example output:

    .. code-block:: html+django

     <script>
      var lookups = ['burglary', 'speeding', 'vandalism'];
     </script>
    """
    if is_instance_of_model(schema_slug, Schema):
        schema_slug = schema_slug.slug
    values = Lookup.objects.filter(schema_field__schema__slug=schema_slug,
                                   schema_field__name=sf_name).values_list('name')
    values = [d[0] for d in values]
    return json.dumps(sorted(values))


def get_locations_for_item(parser, token):
    """
    Tag that puts into the context some data about intersecting locations,
    useful for eg. linking to URLs based on those locations.

    Syntax:

    .. code-block:: html+django

      {% get_locations_for_item newsitem location_type_slug (location_type_slug2 ...) as varname %}

    The ``location_type_slug`` arguments will be used, in the order
    given, to specify which types of locations to find.

    The last argument is the name of the context variable in which to
    put the result.

    For each matching location, the result will contain a dictionary
    with these keys: location_slug, location_name, location_type_slug,
    location_type_name.


    Here's an example template in which we build links for each
    intersecting location:

    .. code-block:: html+django

     {% for item in news_items %}
       {% get_locations_for_item item 'village' 'town' 'city' as locations_info %}
       {% for loc_info in locations_info %}
         <li><a href="http://example.com/yourtown/{{loc_info.location_slug}}">
            Other News in {{ loc_info.location_name }}
         </a></li>
       {% endfor %}
     {% endfor %}

    """
    bits = token.split_contents()
    tagname = bits.pop(0)
    if len(bits) < 4:
        raise template.TemplateSyntaxError('%r tag requires at least 3 arguments' % tagname)
    newsitem = bits[0]
    varname = bits[-1]
    if bits[-2] != 'as':
        raise template.TemplateSyntaxError('%r tag needs args: newsitem slug (slug...) as variable' % tagname)
    loctypes = [s.strip('\'"') for s in bits[1:-2]]
    return LocationInfoNode(newsitem, varname, *loctypes)
register.tag('get_locations_for_item', get_locations_for_item)


class LocationInfoNode(template.Node):
    def __init__(self, newsitem_context_var, varname, *location_type_slugs):
        self.newsitem_context_var = template.Variable(newsitem_context_var)
        self.varname = varname
        self.loctype_slugs = location_type_slugs

    def render(self, context):
        """Puts some information about overlapping locations into context[varname].
        """
        newsitem_context = self.newsitem_context_var.resolve(context)
        if isinstance(newsitem_context, dict):
            newsitem = newsitem_context.get('_item', None)
        else:
            newsitem = newsitem_context
        if not is_instance_of_model(newsitem, NewsItem):
            raise template.TemplateSyntaxError("The newsitem argument to 'get_locations_for_item' tag must be either a NewsItem, or a dictionary eg. as created by the template_context_for_item() function")

        # TODO: cache the LocationType lookup?
        location_types = LocationType.objects.filter(slug__in=self.loctype_slugs)
        loctype_dict = dict([(d['slug'], d)
                             for d in location_types.values('name', 'slug')])
        result = []
        nilocations = newsitem.location_set.all()
        for slug in self.loctype_slugs:
            loctype = loctype_dict.get(slug)
            if loctype is None:
                continue
            locations = nilocations.filter(location_type__slug=loctype['slug'])
            # Assume there is at most one intersecting location of each type.
            # That will probably be wrong somewhere someday...
            # eg. neighborhoods with fuzzy borders.
            locations = list(locations[:1])
            if locations:
                location = locations[0]
                result.append(
                    {'location_slug': location.slug,
                     'location_type_slug': loctype['slug'],
                     'location_type_name': smart_title(loctype['name'], ['ZIP']),
                     'location_name': location.name,
                     }
                    )

        context[self.varname] = result
        return u''

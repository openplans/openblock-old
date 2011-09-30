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

from ebpub.db.models import NewsItem, SchemaField
from ebpub.db.utils import populate_attributes_if_needed
from ebpub.utils.bunch import bunch, bunchlong, stride
from ebpub.metros.allmetros import METRO_LIST, get_metro
from django import template
from django.core.cache import cache
from django.template.defaultfilters import stringfilter
from django.template.loader import select_template
from ebpub.db.utils import today
import datetime
import re

register = template.Library()

register.filter('bunch', bunch)
register.filter('bunchlong', bunchlong)
register.filter('stride', stride)

def METRO_NAME():
    name = get_metro()['metro_name']
    if name[0] != name[0].upper:
        name = name.title()
    return name
register.simple_tag(METRO_NAME)

def isdigit(value):
    return value.isdigit()
isdigit = stringfilter(isdigit)
register.filter('isdigit', isdigit)

def lessthan(value, arg):
    return int(value) < int(arg)
register.filter('lessthan', lessthan)

def greaterthan(value, arg):
    return int(value) > int(arg)
register.filter('greaterthan', greaterthan)

def schema_plural_name(schema, value):
    if isinstance(value, (list, tuple)):
        value = len(value)
    return (value == 1) and schema.name or schema.plural_name
register.simple_tag(schema_plural_name)

def safe_id_sort(value, arg):
    """
    Like Django's built-in "dictsort", but sorts second by the ID attribute, to
    ensure sorts always end up the same.
    """
    var_resolve = template.Variable(arg).resolve
    decorated = [(var_resolve(item), item.id, item) for item in value]
    decorated.sort()
    return [item[2] for item in decorated]
safe_id_sort.is_safe = False
register.filter('safe_id_sort', safe_id_sort)

def safe_id_sort_reversed(value, arg):
    var_resolve = template.Variable(arg).resolve
    decorated = [(var_resolve(item), item.id, item) for item in value]
    decorated.sort()
    decorated.reverse()
    return [item[2] for item in decorated]
safe_id_sort_reversed.is_safe = False
register.filter('safe_id_sort_reversed', safe_id_sort_reversed)

def friendlydate(value):
    """
    A date string that includes 'Today' or 'Yesterday' if relevant,
    or the day of the week if it's within the past week,
    otherwise just the date.

    Examples:

    >>> import mock, datetime
    >>> with mock.patch('ebpub.db.templatetags.eb.today', lambda: datetime.date(2011, 8, 15)):
    ...     print friendlydate(datetime.date(2011, 8, 15))
    ...     print friendlydate(datetime.date(2011, 8, 14))
    ...     print friendlydate(datetime.date(2011, 8, 13))
    ...     print friendlydate(datetime.date(2011, 8, 9))
    ...     print friendlydate(datetime.date(2011, 8, 8))
    ...
    Today August 15, 2011
    Yesterday August 14, 2011
    Saturday August 13, 2011
    Tuesday August 9, 2011
    August 8, 2011
    """
    try: # Convert to a datetime.date, if it's a datetime.datetime.
        value = value.date()
    except AttributeError:
        pass
    # Using value.day because strftine('%d') is zero-padded and we don't want that.
    # TODO: parameterize format to allow i18n?
    formatted_date = value.strftime('%B ') + unicode(value.day) + value.strftime(', %Y')
    _today = today()
    if value == _today:
        return 'Today %s' % formatted_date
    elif value == _today - datetime.timedelta(1):
        return 'Yesterday %s' % formatted_date
    elif _today - value <= datetime.timedelta(6):
        return '%s %s' % (value.strftime('%A'), formatted_date)
    return formatted_date

register.filter('friendlydate', friendlydate)

class GetMetroListNode(template.Node):
    def render(self, context):
        context['METRO_LIST'] = METRO_LIST
        return ''

def do_get_metro_list(parser, token):
    # {% get_metro_list %}
    return GetMetroListNode()
register.tag('get_metro_list', do_get_metro_list)

class GetMetroNode(template.Node):
    def render(self, context):
        context['METRO'] = get_metro()
        return ''

def do_get_metro(parser, token):
    # {% get_metro %}
    return GetMetroNode()
register.tag('get_metro', do_get_metro)

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

def do_get_newsitem(parser, token):
    # {% get_newsitem [id_or_var_containing_id] as [context_var] %}
    bits = token.split_contents()
    if len(bits) != 4:
        raise template.TemplateSyntaxError('%r tag requires 3 arguments' % bits[0])
    return GetNewsItemNode(bits[1], bits[3])
register.tag('get_newsitem', do_get_newsitem)

class GetNewerNewsItemNode(template.Node):
    def __init__(self, newsitem_variable, newsitem_list_variable, context_var):
        self.newsitem_var = template.Variable(newsitem_variable)
        self.newsitem_list_var = template.Variable(newsitem_list_variable)
        self.context_var = context_var

    def render(self, context):
        newsitem = self.newsitem_var.resolve(context)
        newsitem_list = self.newsitem_list_var.resolve(context)
        if newsitem_list and newsitem_list[0].item_date > newsitem.item_date:
            context[self.context_var] = newsitem_list[0]
        else:
            context[self.context_var] = None
        return ''

def do_get_newer_newsitem(parser, token):
    # {% get_more_recent_newsitem [newsitem] [comparison_list] as [context_var] %}
    bits = token.split_contents()
    if len(bits) != 5:
        raise template.TemplateSyntaxError('%r tag requires 4 arguments' % bits[0])
    return GetNewerNewsItemNode(bits[1], bits[2], bits[4])
register.tag('get_newer_newsitem', do_get_newer_newsitem)

class GetNewsItemListByAttributeNode(template.Node):
    def __init__(self, schema_id_variable, newsitem_id_variable, att_name, att_value_variable, context_var):
        self.schema_id_variable = template.Variable(schema_id_variable)
        self.newsitem_id_variable = template.Variable(newsitem_id_variable)
        self.att_name = att_name
        self.att_value_variable = template.Variable(att_value_variable)
        self.context_var = context_var

    def render(self, context):
        schema_id = self.schema_id_variable.resolve(context)
        newsitem_id = self.newsitem_id_variable.resolve(context)
        att_value = self.att_value_variable.resolve(context)
        sf = SchemaField.objects.select_related().get(schema__id=schema_id, name=self.att_name)
        ni_list = NewsItem.objects.select_related().filter(schema__id=schema_id).exclude(id=newsitem_id).by_attribute(sf, att_value).order_by('-item_date')
        populate_attributes_if_needed(ni_list, [sf.schema])

        # We're assigning directly to context.dicts[-1] so that the variable
        # gets set in the top-most context in the context stack. If we didn't
        # do this, the variable would only be available within the specific
        # {% block %} from which the template tag was called, because the
        # {% block %} implementation does a context.push() and context.pop().
        context.dicts[-1][self.context_var] = ni_list

        return ''

def do_get_newsitem_list_by_attribute(parser, token):
    # {% get_newsitem_list_by_attribute [schema_id] [newsitem_id_to_ignore] [att_name]=[value_or_var_containing_value] as [context_var] %}
    # {% get_newsitem_list_by_attribute schema.id newsitem.id business_id=attributes.business_id as other_licenses %}
    bits = token.split_contents()
    if len(bits) != 6:
        raise template.TemplateSyntaxError('%r tag requires 5 arguments' % bits[0])
    if bits[3].count('=') != 1:
        raise template.TemplateSyntaxError('%r tag third argument must contain 1 equal sign' % bits[0])
    att_name, att_value_variable = bits[3].split('=')
    return GetNewsItemListByAttributeNode(bits[1], bits[2], att_name, att_value_variable, bits[5])
register.tag('get_newsitem_list_by_attribute', do_get_newsitem_list_by_attribute)

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

def do_newsitem_list_by_schema(parser, token):
    # {% newsitem_list_by_schema [newsitem_or_newsitem_list] [ungrouped?] %}
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
register.tag('newsitem_list_by_schema', do_newsitem_list_by_schema)

def contains(value, arg):
    return arg in value
register.filter('contains', contains)


class SearchPlaceholderNode(template.Node):
    """
    See do_search_placeholder()
    """
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

def do_search_placeholder(parser, token):
    """
    Stores in the context a list of LocationTypes,
    plus 'address', with an optional prefix.

    Useful for search form widgets where we want to use this as
    placeholder text on the input, and need to write the same string
    over and over because javascript will be checking for the
    placeholder text, restoring it, etc.

    Example::

      {% set_search_placeholder "Some prefix" as some_var %}
      <p>{{ some_var }}</p>

    This will output in the template::

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

register.tag('set_search_placeholder', do_search_placeholder)

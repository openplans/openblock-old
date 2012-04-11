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
Template tags mostly related to the
:py:func:`ebpub.db.views.schema_filter` view:
generating URLs and forms to link/submit to that view.

To use these, your template must include:

.. code-block:: html+django

   {% load eb_filter %}

"""

from django import template
from ebpub.db.models import Schema
from ebpub.db.schemafilters import FilterChain

register = template.Library()

class Base(template.Node):

    def __init__(self, filterchain_var, additions, removals, clear=False):
        self.filterchain_var = template.Variable(filterchain_var)
        self.clear = clear
        # Additions and removals are tuples to make sure we
        # don't do anything non-threadsafe with them during render().
        # http://docs.djangoproject.com/en/dev/howto/custom-template-tags/#thread-safety-considerations
        if clear:
            self.removals = ()
        else:
            self.removals = tuple(template.Variable(r) for r in removals)
        self.additions = []
        for key, values in additions:
            self.additions.append((template.Variable(key),
                                   tuple(template.Variable(v) for v in values),
                                   ))
        self.additions = tuple(self.additions)

    def _get_additions(self, context):
        additions = []
        for key, values in self.additions:
            key = key.resolve(context)
            additions.append((key, [v.resolve(context) for v in values]))
        return additions

    def _get_removals(self, context):
        removals = [r.resolve(context) for r in self.removals]
        return removals

    def _get_filterchain(self, context):
        filterchain_or_schema = self.filterchain_var.resolve(context)
        if isinstance(filterchain_or_schema, FilterChain):
            filterchain = filterchain_or_schema
        elif isinstance(filterchain_or_schema, Schema):
            # Note, context['request'] only works if
            # django.core.context_processors.request is enabled in
            # TEMPLATE_CONTEXT_PROCESSORS.
            filterchain = FilterChain(context=context, request=context.get('request'),
                                      schema=filterchain_or_schema)
        else:
            raise template.TemplateSyntaxError(
                "%r is neither a FilterChain nor a Schema" % filterchain_or_schema)
        if self.clear:
            filterchain = filterchain.copy()
            filterchain.clear()
        return filterchain


class FilterUrlNode(Base):

    # Node for the filter_url tag

    def render(self, context):
        filterchain = self._get_filterchain(context)
        additions = self._get_additions(context)
        removals = self._get_removals(context)
        return filterchain.make_url(additions=additions, removals=removals)


class FilterFormInputsNode(Base):

    # Node for the filter_form_inputs tag

    def render(self, context):
        filterchain = self._get_filterchain(context)
        for key in self._get_removals(context):
            try:
                del filterchain[key]
            except KeyError:
                pass
        for key, values in self._get_additions(context):
            filterchain.replace(key, *values)
        output = ['<!-- filter_form_inputs tag output -->']
        for name, filter in filterchain.items():
            for name, values in filter.get_query_params().items():
                if not isinstance(values, (list, tuple)):
                    values = [values]
                    for v in values:
                        output.append('<input type="hidden" name="%s" value="%s" />'
                                      % (name, v))
        output.append('<!-- end filter_form_inputs -->')
        from django.utils.safestring import mark_safe
        output = '\n'.join(output)
        return mark_safe(output)


def filter_url(parser, token):
    """
    Template tag that outputs a URL based on the filter chain, with
    optional additions/removals of filters.  The first argument is
    required and can be either an existing FilterChain or a Schema:

    .. code-block:: html+django

      {% filter_url filter_chain %}
      {% filter_url schema %}

    To remove a NewsitemFilter from the url, specify the key with a leading "-":

    .. code-block:: html+django

      {% filter_url filter_chain -key_to_remove %}
      {% filter_url filter_chain -"key_to_remove" %}
      {% filter_url filter_chain -key1 -key2 ... %}

    To add NewsitemFilters to the url, specify the key with a leading
    "+", followed by args to use for constructing a NewsitemFilter.

    Keys and values will be passed to FilterChain.add(); see its docs
    for info on legal values. But briefly, the keys are either
    SchemaField instances, or a string understood by SchemaFilter,
    such as 'pubdate':

    .. code-block:: html+django

      {% filter_url filter_chain +"key" value %}
      {% filter_url filter_chain +key value1 value 2 ... %}
      {% filter_url filter_chain +key1 "arg1a" "arg1b" +key2 "arg2a" ... %}

    You can even mix and match additions and removals:

    .. code-block:: html+django

      {% filter_url filter_chain -key1 +key2 arg2 -key3 +key4 arg4 ... %}
    """
    args = _parse(parser, token)
    return FilterUrlNode(*args)



def filter_form_inputs(parser, token):
    """
    Template tag that takes same args as :py:func:`filter_url`, but outputs a set
    of hidden form inputs encapsulating the current filter chain,
    optionally with added or removed filters.

    For example, to make a form that preserves current filters except
    allows choosing a new date range, you would do:

    .. code-block:: html+django

      <form action="{% filter_url filters.schema %}">
         {% filter_form_inputs filters -"date" %}
         <input type="text" name="start_date">
         <input type="text" name="end_date">
         <input type="submit">
      </form>

    In this example,
    the form action URL is generated by ``filter_url`` with just the schema,
    and all non-date current filters are inserted by using
    ``filter_form_inputs`` on the second line.
    The new dates are given by normal non-hidden form fields.
    """
    args = _parse(parser, token)
    return FilterFormInputsNode(*args)


def _parse(parser, token):
    # Handle parsing of filter_url and filter_form_inputs tags.
    bits = token.split_contents()
    additions, removals = [], []
    try:
        filterchain_var = bits[1]
    except IndexError:
        raise template.TemplateSyntaxError('Missing required filterchain argument')
    # TODO: This probably fails for removals of hard-coded strings that contain spaces.
    bits = bits[2:]
    clear = False
    while bits:
        bit = bits.pop(0)
        if bit.startswith('-'):
            key = bit[1:]
            if not len(key):
                raise template.TemplateSyntaxError('Invalid argument: %r' % bit)
            if key == 'all':
                removals = []
                clear=True
            else:
                removals.append(key)
        elif bit.startswith('+'):
            key = bit[1:]
            if not len(key):
                raise template.TemplateSyntaxError('Invalid argument: %r' % bit)
            values = []
            while bits:
                # Consume all remaining args until the next addition/removal.
                if bits[0][0] in ('+', '-'):
                    break
                values.append(bits.pop(0))
            # if not len(values):
            #     raise template.TemplateSyntaxError('Invalid argument: %r' % bit)
            additions.append((key, values))
        else:
            raise template.TemplateSyntaxError('Invalid argument: %r' % bit)
    return (filterchain_var, additions, removals, clear)


register.tag('filter_url', filter_url)
register.tag('filter_form_inputs', filter_form_inputs)

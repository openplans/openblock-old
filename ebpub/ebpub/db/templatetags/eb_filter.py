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
Template tags for the custom filter.
"""

from django import template
from ebpub.db.models import Schema
from ebpub.db.schemafilters import FilterChain

register = template.Library()

class FilterUrlNode(template.Node):
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

    def render(self, context):
        filterchain = self.filterchain_var.resolve(context)
        if isinstance(filterchain, FilterChain):
            schema = filterchain.schema
        elif isinstance(filterchain, Schema):
            schema = filterchain
            # Note, context['request'] only works if
            # django.core.context_processors.request is enabled in
            # TEMPLATE_CONTEXT_PROCESSORS.
            filterchain = FilterChain(context=context, request=context['request'],
                                      schema=schema)
        else:
            raise template.TemplateSyntaxError(
                "%r is neither a FilterChain nor a Schema" % filterchain)
        removals = [r.resolve(context) for r in self.removals]
        if self.clear:
            filterchain = filterchain.copy()
            filterchain.clear()
        additions = []
        for key, values in self.additions:
            key = key.resolve(context)
            additions.append((key, [v.resolve(context) for v in values]))
        schema = filterchain.schema
        return filterchain.make_url(additions=additions, removals=removals)

def do_filter_url(parser, token):
    """
    Outputs a URL based on the filter chain, with optional
    additions/removals of filters.  The first argument is required
    and can be either an existing FilterChain or a Schema.

    {% filter_url filter_chain %}
    {% filter_url schema %}

    To remove a NewsitemFilter from the url, specify the key with a leading "-".

    {% filter_url filter_chain -key_to_remove %}
    {% filter_url filter_chain -"key_to_remove" %}
    {% filter_url filter_chain -key1 -key2 ... %}

    To add NewsitemFilters to the url, specify the key with a leading "+",
    followed by args to use for constructing a NewsitemFilter.

    {% filter_url filter_chain +"key" value %}
    {% filter_url filter_chain +key value1 value 2 ... %}
    {% filter_url filter_chain +key1 "arg1a" "arg1b" +key2 "arg2a" ... %}

    You can even mix and match additions and removals:

    {% filter_url filter_chain -key1 +key2 arg2 -key3 +key4 arg4 ... %}
    """
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
    return FilterUrlNode(filterchain_var, additions, removals, clear=clear)

register.tag('filter_url', do_filter_url)

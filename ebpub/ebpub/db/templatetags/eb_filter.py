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

register = template.Library()

def filter_breadcrumb_link(schema, filters, filter_):
    """
    {% filter_breadcrumb_link filters filter %}
    """
    output = []
    for f in filters:
        output.append(f['url'])
        if f == filter_:
            break
    return '%s%s/' % (schema.url(), '/'.join(output))
register.simple_tag(filter_breadcrumb_link)

class FilterUrlNode(template.Node):
    def __init__(self, schema_var, filterdict_var, additions, removals):
        self.schema_var = template.Variable(schema_var)
        self.filterdict_var = template.Variable(filterdict_var)
        self.additions = [(template.Variable(k), template.Variable(v)) for k, v in additions]
        self.removals = [template.Variable(a) for a in removals]

    def render(self, context):
        # Note that we do a copy() here so that we don't edit the dict in place.
        schema = self.schema_var.resolve(context)
        filterdict = self.filterdict_var.resolve(context).copy()
        for key, value in self.additions:
            filterdict[key.resolve(context)] = value.resolve(context)
        for key in self.removals:
            try:
                del filterdict[key.resolve(context)]
            except KeyError:
                pass
        urls = [d['url'] for d in filterdict.values()]
        if urls:
            return '%s%s/' % (schema.url(), ';'.join(urls))
        else:
            return '%sfilter/' % schema.url()

def do_filter_url(parser, token):
    """
    {% filter_url schema filter_dict %}
    {% filter_url schema filter_dict key value %}
    {% filter_url schema filter_dict key "value again" %}
    {% filter_url schema filter_dict "key" "value again" %}
    {% filter_url schema filter_dict -key_to_remove %}
    {% filter_url schema filter_dict -"key_to_remove" %}

    Outputs a string like '/filter1=foo;filter2=bar/' (with a trailing slash but
    not a leading slash).
    """
    bits = token.split_contents()
    additions, removals = [], []
    schema_var = bits[1]
    filterdict_var = bits[2]
    stack = bits[:2:-1]
    # TODO: This probably fails for removals of hard-coded strings that contain spaces.
    while stack:
        bit = stack.pop()
        if bit.startswith('-'):
            removals.append(bit[1:])
        else:
            try:
                next_bit = stack.pop()
            except IndexError:
                raise template.TemplateSyntaxError('Invalid argument length: %r' % token)
            additions.append((bit, next_bit))
    return FilterUrlNode(schema_var, filterdict_var, additions, removals)

register.tag('filter_url', do_filter_url)

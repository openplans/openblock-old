#   Copyright 2011 OpenPlans and contributors
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
Breadcrumbs helpers.
These functions return lists of (label, url) pairs.
"""

from django.core import urlresolvers
from ebpub.metros.allmetros import get_metro

def home(context):
    return [(get_metro()['metro_name'], urlresolvers.reverse('ebpub-homepage'),)]

def location_type_detail(context):
    crumbs = home(context)
    location_type = context['location_type']
    crumbs.append((location_type.plural_name, location_type.url()))
    return crumbs

def street_list(context):
    crumbs = home(context)
    crumbs.append((u'Streets', '/streets/'))
    if get_metro()['multiple_cities']: # XXX UNTESTED
        city = context.get('city')
        if city is None:
            if context.get('place_type') == 'block':
                city = context['place'].city_object()
            else:
                assert False, "context has neither city nor a place from which to get it"
        crumbs.append((city.name, "/streets/%s/" % city.slug))
    return crumbs

def block_list(context):
    block = context.get('first_block')
    if block is None:
        if context.get('place_type') == 'block':
            block = context['place']
        else:
            assert False, "context has neither first_block nor a block-type place"
    crumbs = street_list(context)
    crumbs.append((block.street_pretty_name, block.street_url()))
    return crumbs

def place_base(context):
    place = context['place']
    if context['is_block']:
        crumbs = block_list(context)
    else:
        context['location_type'] = place.location_type
        crumbs = location_type_detail(context)
    crumbs.append((place.pretty_name, place.url()))
    return crumbs

def place_detail_timeline(context):
    crumbs =  place_base(context)
    crumbs.append(('Recent: Everything', ''))
    return crumbs

def place_detail_upcoming(context):
    crumbs =  place_base(context)
    crumbs.append(('Upcoming: Everything', ''))
    return crumbs

def place_detail_overview(context):
    crumbs =  place_base(context)
    crumbs.append(('Overview', ''))
    return crumbs


def schema_detail(context):
    crumbs = home(context)
    schema = context['schema']
    crumbs.append((schema.plural_name,
                   urlresolvers.reverse('ebpub-schema-detail', args=(context['schema'].slug,))))
    return crumbs

def schema_about(context):
    crumbs = schema_detail(context)
    crumbs.append(('About',
                   urlresolvers.reverse('ebpub-schema-about', args=(context['schema'].slug,))))
    return crumbs

def schema_filter(context):
    crumbs = schema_detail(context)
    crumbs.append(('Search', ''))
    # This one's a generator because we want to evaluate it lazily,
    # and django's 'for' template tag doesn't accept callables.
    for crumb in crumbs:
        yield crumb

def newsitem_detail(context):
    context['schema'] = context['newsitem'].schema
    return schema_filter(context)

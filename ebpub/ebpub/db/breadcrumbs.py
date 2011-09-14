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
    filterchain = context.get('filters')
    if filterchain is not None:
        url = crumbs[-1][1]
        crumbs += filterchain.make_breadcrumbs(base_url=url)
    # This one's a generator because we want to evaluate it lazily,
    # and django's 'for' template tag doesn't accept callables.
    for crumb in crumbs:
        yield crumb

def newsitem_detail(context):
    context['schema'] = context['newsitem'].schema
    return schema_filter(context)

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

from django import template
from ebpub.db.models import Location, LocationType
from ebpub.utils.text import smart_title

register = template.Library()


def do_item_locations(parser, token):
    """
    Puts into the context some data about intersecting locations,
    useful for eg. linking to URLs based on those locations.

    {% get_locations_for_item newsitem location_type_slug (location_type_slug2 ...) as varname %}

    The ``location_type_slug`` arguments will be used, in the order
    given, to specify which types of locations to find.

    The last argument is the name of the context variable in which to
    put the result.

    For each matching location, the result will contain a dictionary
    with these keys: location_slug, location_name, location_type_slug,
    location_type_name.


    Here's an example template in which we build links for each
    intersecting location::

     {% for item in news_items %}
       {% get_locations_for_item item 'village' 'town' 'city' as locations_info %}
       {% for loc_info in locations_info %}
         <li><a href="http://example.com/yourtown/{{ loc_info.location_slug}}"> Other News in {{ loc_info.location_name }}</a></li>
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
register.tag('get_locations_for_item', do_item_locations)


class LocationInfoNode(template.Node):
    def __init__(self, newsitem_context_var, varname, *location_type_slugs):
        self.newsitem_context_var = template.Variable(newsitem_context_var)
        self.varname = varname
        self.loctype_slugs = location_type_slugs

    def render(self, context):
        """Puts some information about overlapping locations into context[varname].
        """
        newsitem_context = self.newsitem_context_var.resolve(context)
        if not isinstance(newsitem_context, dict):
            raise template.TemplateSyntaxError("The newsitem argument to 'get_locations_for_item' tag must be a dictionary eg. as created by the template_context_for_item() function")
        # TODO: cache the LocationType lookup?
        location_types = LocationType.objects.filter(slug__in=self.loctype_slugs)
        loctype_dict = dict([(d['slug'], d)
                             for d in location_types.values('name', 'slug')])
        result = []
        newsitem = newsitem_context['_item']
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

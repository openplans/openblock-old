#   Copyright 2012 OpenPlans, and contributors
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

from django.conf import settings
from ebpub.db.schemafilters import FilterChain

def _get_featured_categories():
    from ebpub.db.models import Lookup
    lookups = {}
    for lookup in Lookup.objects.filter(featured=True).select_related():
        lookup = lookup.lookup
        sf = lookup.schema_field
        schema = sf.schema
        filters = FilterChain(schema=schema)
        filters.add(sf, lookup)
        info = {'lookup': lookup.name, 'url': filters.make_url()}
        lookups.setdefault(schema.slug, []).append(info)
    return lookups

def neighbornews_context(request):
    """
    Lazy context variables for NeighborNews.

    This way, they're always available if you want them, and
    if you don't, they don't hurt performance.
    """
    if 'ebpub.neighbornews' in settings.INSTALLED_APPS:
        return {
            'featured_categories': _get_featured_categories,
            }
    else:
        return {}

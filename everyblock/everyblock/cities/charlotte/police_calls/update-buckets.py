#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of everyblock
#
#   everyblock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   everyblock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with everyblock.  If not, see <http://www.gnu.org/licenses/>.
#

from ebpub.db.models import NewsItem, SchemaField, Lookup
from everyblock.cities.charlotte.police_calls.retrieval import CATEGORIES
from django.template.defaultfilters import capfirst

if __name__ == '__main__':
    schema_slug = 'police-calls'
    schema_field = SchemaField.objects.get(schema__slug=schema_slug, name='category')
    for ni in NewsItem.objects.filter(schema__slug=schema_slug):
        event = Lookup.objects.get(pk=ni.attributes['event'])
        category_code = CATEGORIES[event.name.upper()]
        category_name = capfirst(category_code.lower())
        bucket = Lookup.objects.get_or_create_lookup(schema_field, category_name, category_code)
        old_bucket_id = ni.attributes['category']
        if old_bucket_id is None or bucket.id != old_bucket_id:
            ni.attributes['category'] = bucket.id
            print "Bucket changed"
            print old_bucket_id
            print bucket

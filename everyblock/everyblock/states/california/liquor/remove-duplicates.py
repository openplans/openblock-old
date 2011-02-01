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

from ebpub.db.models import Schema, NewsItem, Lookup

schema = Schema.objects.get(slug='liquor-licenses')
schema_fields = {}
for f in schema.schemafield_set.all():
    schema_fields[f.name] = f

# Run over the newsitems in reverse id order, if any duplicated were found for
# the current newsitem, delete the newsitem. This way, we will look at each
# newsitem once, and nothing will be deleted before we get to it in the loop.

for ni in NewsItem.objects.filter(schema=schema).order_by('-id').iterator():
    qs = NewsItem.objects.filter(schema=schema, item_date=ni.item_date).exclude(id=ni.id)
    qs = qs.by_attribute(schema_fields['page_id'], ni.attributes['page_id'])
    qs = qs.by_attribute(schema_fields['type'], ni.attributes['type'])

    record_type = Lookup.objects.get(pk=ni.attributes['record_type'])

    if record_type.code == 'STATUS_CHANGE':
        qs = qs.by_attribute(schema_fields['old_status'], ni.attributes['old_status'])
        qs = qs.by_attribute(schema_fields['new_status'], ni.attributes['new_status'])
    else:
        qs = qs.by_attribute(schema_fields['action'], ni.attributes['action'])

    duplicate_count = qs.count()
    if duplicate_count > 0:
        ni.delete()
        print "Deleting %s because %s duplicates were found." % (ni, duplicate_count)
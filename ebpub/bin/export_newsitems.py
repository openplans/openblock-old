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
Exports newsitems to a CSV file.
"""

from ebpub.db.models import NewsItem, Location, Schema
import sys
import csv
from optparse import OptionParser

def export_newsitems(queryset, schema, out):
    ni_fields = [('title', 'title'),
                 ('description', 'description'),
                 ('location_name', 'location'),
                 ('url', 'URL'),
                 ('item_date', 'item date'),
                 ('pub_date', 'publication date')]
    s_fields = [(str(sf.name), str(sf.pretty_name)) for sf in schema.schemafield_set.all()]
    s_fields.sort()
    writer = csv.writer(out)
    writer.writerow([f[1] for f in ni_fields + s_fields])
    for ni in queryset:
        values = [getattr(ni, f[0]) for f in ni_fields]
        values += [ni.attributes[f[0]] for f in s_fields]
        writer.writerow(values)

def main():
    parser = OptionParser(usage='usage: %prog [options] <schema-slug>')
    parser.add_option('-l', '--location', dest='loc_slug', metavar="SLUG",
                      help='limit newsitems to those contained by location')
    parser.add_option('-f', '--filename', dest='out_file', metavar="FILE",
                      help='write output to this filename')

    (options, args) = parser.parse_args()

    if not args:
        parser.error('must give a schema slug')

    try:
        schema = Schema.objects.get(slug=args[0])
    except Schema.DoesNotExist:
        parser.error('unknown schema %r' % args[0])
        return 1

    niqs = NewsItem.objects.filter(schema=schema)

    if options.loc_slug:
        try:
            loc = Location.objects.get(slug=options.loc_slug)
        except Location.DoesNotExist:
            parser.error('unknown location %r' % options.loc_slug)
            return 1
        else:
            niqs = niqs.filter(location__within=loc.location)

    if options.out_file:
        f = open(options.out_file, 'w')
    else:
        f = sys.stdout

    export_newsitems(niqs, schema, f)

if __name__ == '__main__':
    sys.exit(main())
    

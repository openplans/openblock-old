#!/usr/bin/env python
import os
import sys
import datetime
from optparse import OptionParser
from django.contrib.gis.gdal import DataSource
from django.db import connection
from ebpub.db.models import Location, LocationType, NewsItem
from ebpub.geocoder.parser.parsing import normalize
from ebpub.utils.text import slugify
from ebpub.metros.allmetros import get_metro

def populate_ni_loc(location):
    """
    Add NewsItemLocations for all NewsItems that overlap with the new
    Location.
    """
    ni_count = NewsItem.objects.count()
    cursor = connection.cursor()
    i = 0
    while i < ni_count:
        cursor.execute("""
            INSERT INTO db_newsitemlocation (news_item_id, location_id)
            SELECT ni.id, loc.id FROM db_newsitem ni, db_location loc
            WHERE st_intersects(loc.location, ni.location)
                AND ni.id >= %s AND ni.id < %s
                AND loc.id = %s
        """, (i, i+200, location.id))
        connection._commit()
        i += 200

class LocationImporter(object):
    def __init__(self, layer, location_type):
        self.layer = layer
        metro = get_metro()
        self.metro_name = metro['metro_name'].upper()
        self.now = datetime.datetime.now()
        self.location_type = location_type

    def save(self, name_field='name', source='UNKNOWN', verbose=True):
        locs = []
        for feature in self.layer:
            name = feature.get(name_field)
            geom = feature.geom.transform(4326, True).geos
            if not geom.valid:
                geom = geom.buffer(0.0)
                if not geom.valid:
                    print >> sys.stderr, 'Warning: invalid geometry: %s' % name
            fields = dict(
                name = name,
                normalized_name = normalize(name),
                slug = slugify(name),
                location_type = self.location_type,
                location = geom,
                centroid = geom.centroid,
                city = self.metro_name,
                source = source,
                area = geom.transform(3395, True).area,
                is_public = True,
                display_order = 0, # This is overwritten in the next loop
            )
            locs.append(fields)
        num_created = 0
        for i, loc_fields in enumerate(sorted(locs, key=lambda h: h['name'])):
            kwargs = dict(loc_fields, defaults={'creation_date': self.now, 'last_mod_date': self.now, 'display_order': i})
            loc, created = Location.objects.get_or_create(**kwargs)
            if created:
                num_created += 1
            if verbose:
                print >> sys.stderr, '%s %s %s' % (created and 'Created' or 'Already had', self.location_type.name, loc)
            if verbose:
                sys.stderr.write('Populating newsitem locations ... ')
            populate_ni_loc(loc)
            if verbose:
                sys.stderr.write('done.\n')
        return num_created

usage = 'usage: %prog [options] type_slug /path/to/shapefile'
optparser = OptionParser(usage=usage)

def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    optparser.add_option('--type-name', dest='type_name', default='', help='specifies the location type name')
    optparser.add_option('--type-name-plural', dest='type_name_plural', default='', help='specifies the location type plural name')
    optparser.add_option('-n', '--name-field', dest='name_field', default='name', help='field that contains location\'s name')
    optparser.add_option('-i', '--layer-index', dest='layer_id', default=0, help='index of layer in shapefile')
    optparser.add_option('-s', '--source', dest='source', default='UNKNOWN', help='source metadata of the shapefile')
    optparser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='be verbose')

    return optparser.parse_args(argv)

def main():
    opts, args = parse_args()
    if len(args) != 2:
        optparser.error('must supply type slug and path to shapefile')
    type_slug = args[0]
    shapefile = args[1]
    if not os.path.exists(shapefile):
        optparser.error('file does not exist')
    ds = DataSource(shapefile)
    layer = ds[opts.layer_id]

    metro = get_metro()
    metro_name = metro['metro_name'].upper()
    location_type, _ = LocationType.objects.get_or_create(
        name = opts.type_name,
        plural_name = opts.type_name_plural,
        scope = metro_name,
        slug = type_slug,
        is_browsable = True,
        is_significant = True,
    )

    importer = LocationImporter(layer, location_type)
    num_created = importer.save(name_field=opts.name_field, source=opts.source, verbose=opts.verbose)
    if opts.verbose:
        print >> sys.stderr, 'Created %s %s.' % (num_created, location_type.plural_name)

if __name__ == '__main__':
    sys.exit(main())
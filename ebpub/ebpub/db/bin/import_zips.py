#!/usr/bin/env python
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


import datetime
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon
from ebpub.db.models import Location, LocationType
from ebpub.metros.allmetros import get_metro
from ebpub.db.bin import import_locations
import os
import sys


class ZipImporter(import_locations.LocationImporter):
    def __init__(self, shapefile, opts):
        location_type, _ = LocationType.objects.get_or_create(
            name = 'ZIP Code',
            plural_name = 'ZIP Codes',
            scope = 'U.S.A.',
            slug = 'zipcodes',
            is_browsable = True,
            is_significant = True,
        )
        ds = DataSource(shapefile)
        layer = ds[opts.layer_id]
        super(ZipImporter, self).__init__(layer, location_type, opts)

    def save(self):
        # The ESRI ZIP Code layer breaks ZIP Codes up along county
        # boundaries, so we need to collapse them first before
        # proceeding
        verbose = self.opts.verbose
        name_field = self.opts.name_field
        source = self.opts.source
        zipcodes = {}
        for feature in self.layer:
            zipcode = feature.get(name_field)
            geom = feature.geom.geos
            if zipcode not in zipcodes:
                zipcodes[zipcode] = geom
            else:
                # If it's a MultiPolygon geom we're adding to our
                # existing geom, we need to "unroll" it into its
                # constituent polygons 
                if isinstance(geom, MultiPolygon):
                    subgeoms = list(geom)
                else:
                    subgeoms = [geom]
                existing_geom = zipcodes[zipcode]
                if not isinstance(existing_geom, MultiPolygon):
                    new_geom = MultiPolygon([existing_geom])
                    new_geom.extend(subgeoms)
                    zipcodes[zipcode] = new_geom
                else:
                    existing_geom.extend(subgeoms)

        sorted_zipcodes = sorted(zipcodes.iteritems(), key=lambda x: int(x[0]))
        now = datetime.datetime.now()
        num_created = 0
        for i, (zipcode, geom) in enumerate(sorted_zipcodes):
            if not geom.valid:
                geom = geom.buffer(0.0)
                if not geom.valid:
                    print >> sys.stderr, 'Warning: invalid geometry for %s' % zipcode
            geom.srid = 4326
            kwargs = dict(
                name = zipcode,
                normalized_name = zipcode,
                slug = zipcode,
                location_type = self.location_type,
                location = geom,
                centroid = geom.centroid,
                display_order = i,
                city = self.metro_name,
                source = source,
                area = geom.transform(3395, True).area,
                is_public = True,
                creation_date = now,
                last_mod_date = now,
            )
            if not self.should_create_location(kwargs):
                continue
            zipcode_obj, created = Location.objects.get_or_create(**kwargs)
            if created:
                num_created += 1
            if verbose:
                print >> sys.stderr, '%s ZIP Code %s ' % (created and 'Created' or 'Already had', zipcode_obj.name)
        return num_created

usage = 'usage: %prog [options] /path/to/shapefile'

optparser = import_locations.optparser

def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    optparser.set_usage(usage)
    optparser.remove_option('-n')
    optparser.add_option('-n', '--name-field', dest='name_field', default='ZCTA5CE',
                         help='field that contains the zipcode\'s name')
    return optparser.parse_args(argv)

def main():
    opts, args = parse_args()
    if len(args) != 1:
        optparser.error('must give path to shapefile')
    shapefile = args[0]
    if not os.path.exists(shapefile):
        optparser.error('file does not exist')
    importer = ZipImporter(shapefile, opts)
    num_created = importer.save()
    if opts.verbose:
        print >> sys.stderr, 'Created %s zipcodes.' % num_created

if __name__ == '__main__':
    sys.exit(main())

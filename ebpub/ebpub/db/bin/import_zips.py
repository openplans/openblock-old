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
from django.contrib.gis.geos import MultiPolygon
from ebpub.db.models import Location, LocationType
from ebpub.utils.geodjango import ensure_valid
from ebpub.utils.geodjango import flatten_geomcollection
from ebpub.db.bin import import_locations
import sys


class ZipImporter(import_locations.LocationImporter):
    def __init__(self, layer, name_field, source='UNKNOWN', filter_bounds=False, verbose=False):
        location_type, _ = LocationType.objects.get_or_create(
            name = 'ZIP Code',
            plural_name = 'ZIP Codes',
            scope = 'U.S.A.',
            slug = 'zipcodes',
            is_browsable = True,
            is_significant = True,
        )
        self.name_field = name_field
        super(ZipImporter, self).__init__(layer, location_type, source, filter_bounds, verbose)
        self.zipcodes = {}
        self.collapse_zip_codes()

    def collapse_zip_codes(self):
        # The ESRI ZIP Code layer breaks ZIP Codes up along county
        # boundaries, so we need to collapse them first before
        # proceeding

        if len(self.zipcodes) > 0:
            return

        for feature in self.layer:
            zipcode = feature.get(self.name_field)
            geom = feature.geom.geos
            if zipcode not in self.zipcodes:
                self.zipcodes[zipcode] = geom
            else:
                # If it's a MultiPolygon geom we're adding to our
                # existing geom, we need to "unroll" it into its
                # constituent polygons 
                if isinstance(geom, MultiPolygon):
                    subgeoms = list(geom)
                else:
                    subgeoms = [geom]
                existing_geom = self.zipcodes[zipcode]
                if not isinstance(existing_geom, MultiPolygon):
                    new_geom = MultiPolygon([existing_geom])
                    new_geom.extend(subgeoms)
                    self.zipcodes[zipcode] = new_geom
                else:
                    existing_geom.extend(subgeoms)

    def create_location(self, zipcode, geom, display_order=0):
        verbose = self.verbose
        source = self.source
        geom = ensure_valid(geom, self.location_type.slug)
        geom = flatten_geomcollection(geom)
        geom.srid = 4326
        kwargs = dict(
            name = zipcode,
            normalized_name = zipcode,
            slug = zipcode,
            location_type = self.location_type,
            location = geom,
            city = self.metro_name,
            source = source,
            is_public = True,
        )
        if not self.should_create_location(kwargs):
            return
        kwargs['defaults'] = {'display_order': display_order,
                              'last_mod_date': self.now,
                              'creation_date': self.now,
                              'area': kwargs['location'].transform(3395, True).area,
                              }
        zipcode_obj, created = Location.objects.get_or_create(**kwargs)
        if verbose:
            print >> sys.stderr, '%s ZIP Code %s ' % (created and 'Created' or 'Already had', zipcode_obj.name)
        return created

    def import_zip(self, zipcode):
        self.create_location(zipcode, self.zipcodes[zipcode])

    def save(self):
        num_created = 0
        sorted_zipcodes = sorted(self.zipcodes.iteritems(), key=lambda x: int(x[0]))
        for i, (zipcode, geom) in enumerate(sorted_zipcodes):
            created = self.create_location(zipcode, geom, display_order=i)
            if created:
                num_created += 1
        return num_created

def parse_args(optparser, argv):
    optparser.set_usage('usage: %prog [options] /path/to/shapefile')
    optparser.remove_option('-n')
    optparser.add_option('-n', '--name-field', dest='name_field', default='ZCTA5CE',
                         help='field that contains the zipcode\'s name')
    opts, args = optparser.parse_args(argv)

    if len(args) != 1:
        optparser.error('must give path to shapefile')

    layer = import_locations.layer_from_shapefile(args[0], opts.layer_id)

    return layer, opts

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    layer, opts = parse_args(import_locations.optparser, argv)
    importer = ZipImporter(layer, opts.name_field, opts.source, opts.filter_bounds, opts.verbose)
    num_created = importer.save()
    if opts.verbose:
        print >> sys.stderr, 'Created %s zipcodes.' % num_created

if __name__ == '__main__':
    sys.exit(main())

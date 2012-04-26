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


"""Script to import ZIP code Locations from a shapefile.
See :ref:`zipcodes`
"""

from django.contrib.gis.geos import MultiPolygon
from ebpub.db.models import LocationType
from ebpub.db.bin import import_locations
from ebpub.utils.geodjango import geos_with_projection
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
        self.zipcode_geoms = {}
        self.collapse_zip_codes()

    def collapse_zip_codes(self):
        # The ESRI ZIP Code layer breaks ZIP Codes up along county
        # boundaries, so we need to collapse them first before
        # proceeding.

        if len(self.zipcode_geoms) > 0:
            return

        for feature in self.layer:
            zipcode = feature.get(self.name_field)
            geom = geos_with_projection(feature.geom)
            if zipcode not in self.zipcode_geoms:
                self.zipcode_geoms[zipcode] = geom
            else:
                # If it's a MultiPolygon geom we're adding to our
                # existing geom, we need to "unroll" it into its
                # constituent polygons 
                if isinstance(geom, MultiPolygon):
                    subgeoms = list(geom)
                else:
                    subgeoms = [geom]
                existing_geom = self.zipcode_geoms[zipcode]
                if not isinstance(existing_geom, MultiPolygon):
                    new_geom = MultiPolygon([existing_geom])
                    new_geom.extend(subgeoms)
                    self.zipcode_geoms[zipcode] = new_geom
                else:
                    existing_geom.extend(subgeoms)


    def import_zip(self, zipcode, display_order=0):
        if zipcode not in self.zipcode_geoms:
            import_locations.logger.info("Zipcode %s not found in shapefile" % zipcode)
            return False
        return self.create_location(zipcode, self.location_type,
                                    geom=self.zipcode_geoms[zipcode],
                                    display_order=display_order)

    def save(self):
        num_created = 0
        num_updated = 0
        sorted_zipcodes = sorted(self.zipcode_geoms.iteritems(), key=lambda x: int(x[0]))
        for i, (zipcode, geom) in enumerate(sorted_zipcodes):
            created = self.create_location(zipcode, self.location_type, geom=geom,
                                           display_order=i)
            if created:
                num_created += 1
            else:
                num_updated += 1
        return (num_created, num_updated)


def parse_args(optparser, argv):
    optparser.set_usage('usage: %prog [options] /path/to/shapefile')
    optparser.remove_option('-n')
    optparser.add_option('-n', '--name-field', dest='name_field', default='ZCTA5CE',
                         help='field that contains the zipcode\'s name')
    opts, args = optparser.parse_args(argv)
    if not opts.verbose:
        import logging
        logging.basicConfig()
        import_locations.logger.setLevel(logging.WARN)

    if len(args) != 1:
        optparser.error('must give path to shapefile')

    layer = import_locations.layer_from_shapefile(args[0], opts.layer_id)

    return layer, opts

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    layer, opts = parse_args(import_locations.optparser, argv)
    importer = ZipImporter(layer, opts.name_field, opts.source, opts.filter_bounds, opts.verbose)
    num_created, num_updated = importer.save()
    if opts.verbose:
        print >> sys.stderr, 'Created %s, updated %s zipcodes.' % (num_created, num_updated)

if __name__ == '__main__':
    sys.exit(main())

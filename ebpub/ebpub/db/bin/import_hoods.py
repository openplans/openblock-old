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

import os
import sys
from django.contrib.gis.gdal import DataSource
from ebpub.db.models import LocationType
from ebpub.db.bin import import_locations
from ebpub.metros.allmetros import get_metro

def parse_args(optparser, argv):
    optparser.set_usage('usage: %prog [options] /path/to/shapefile')
    opts, args = optparser.parse_args(argv)

    if len(args) != 1:
        optparser.error('must give path to shapefile')

    layer = import_locations.layer_from_shapefile(args[0], opts.layer_id)

    return layer, opts

def location_type():
    metro = get_metro()
    metro_name = metro['metro_name'].upper()
    location_type, _ = LocationType.objects.get_or_create(
        name = 'Neighborhood',
        plural_name = 'Neighborhoods',
        scope = metro_name,
        slug = 'neighborhoods',
        is_browsable = True,
        is_significant = True,
    )
    return location_type

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    layer, opts = parse_args(import_locations.optparser, argv)
    importer = import_locations.LocationImporter(
        layer,
        location_type(),
        opts.source,
        opts.filter_bounds,
        opts.verbose
    )
    num_created = importer.save(opts.name_field)
    if opts.verbose:
        print >> sys.stderr, 'Created %s neighborhoods.' % num_created

if __name__ == '__main__':
    sys.exit(main())

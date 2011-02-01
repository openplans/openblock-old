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
import datetime
from optparse import OptionParser
from django.contrib.gis.gdal import DataSource
from django.db import connection
from ebpub.db.models import Location, LocationType, NewsItem
from ebpub.db.bin.import_locations import LocationImporter
from ebpub.metros.allmetros import get_metro

usage = 'usage: %prog [options] /path/to/shapefile'
optparser = OptionParser(usage=usage)

def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    optparser.add_option('-n', '--name-field', dest='name_field', default='name', help='field that contains neighborhood\'s name')
    optparser.add_option('-i', '--layer-index', dest='layer_id', default=0, help='index of layer in shapefile')
    optparser.add_option('-s', '--source', dest='source', default='UNKNOWN', help='source metadata of the shapefile')
    optparser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='be verbose')

    return optparser.parse_args(argv)

def main():
    opts, args = parse_args()
    if len(args) != 1:
        optparser.error('must give path to shapefile')
    shapefile = args[0]
    if not os.path.exists(shapefile):
        optparser.error('file does not exist')
    ds = DataSource(shapefile)
    layer = ds[opts.layer_id]
    
    metro = get_metro()
    metro_name = metro['metro_name'].upper()
    location_type, _ = LocationType.objects.get_or_create(
        name = 'neighborhood',
        plural_name = 'neighborhoods',
        scope = metro_name,
        slug = 'neighborhoods',
        is_browsable = True,
        is_significant = True,
    )
    
    importer = LocationImporter(layer, location_type)
    num_created = importer.save(name_field=opts.name_field, source=opts.source, verbose=opts.verbose)
    if opts.verbose:
        print >> sys.stderr, 'Created %s neighborhoods.' % num_created

if __name__ == '__main__':
    sys.exit(main())

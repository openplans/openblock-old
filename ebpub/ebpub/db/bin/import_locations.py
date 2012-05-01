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


"""
Script to import Locations from a shapefile.
See :ref:`import_locations_from_shapefile`

"""
import os
import sys
import datetime
from optparse import OptionParser
from django.contrib.gis.gdal import DataSource
from django.db import connection
from django.db.utils import IntegrityError
from ebpub.db.models import Location, LocationType, NewsItem, NewsItemLocation
from ebpub.geocoder.parser.parsing import normalize
from ebpub.utils.text import slugify
from ebpub.utils.geodjango import ensure_valid
from ebpub.utils.geodjango import flatten_geomcollection
from ebpub.utils.geodjango import geos_with_projection
from ebpub.metros.allmetros import get_metro

import logging
logger = logging.getLogger('ebpub.db.bin.import_locations')

def populate_ni_loc(location):
    """
    Add NewsItemLocations for all NewsItems that overlap with the new
    Location.
    """
    ni_count = NewsItem.objects.count()
    cursor = connection.cursor()
    # In case the location is not new...
    NewsItemLocation.objects.filter(location=location).delete()
    old_niloc_count = NewsItemLocation.objects.count()
    i = 0
    batch_size = 400
    while i < ni_count:
        # We don't use intersecting_collection() because we should have cleaned up
        # all our geometries by now and it's sloooow ... there could be millions
        # of db_newsitem rows.
        cursor.execute("""
            INSERT INTO db_newsitemlocation (news_item_id, location_id)
            SELECT ni.id, loc.id FROM db_newsitem ni, db_location loc
            WHERE st_intersects(ni.location, loc.location)
                AND ni.id >= %s AND ni.id < %s
                AND loc.id = %s
        """, (i, i + batch_size, location.id))
        connection._commit()
        i += batch_size
    new_count = NewsItemLocation.objects.count()
    logger.info("New: %d NewsItemLocations" % (new_count - old_niloc_count))


class LocationImporter(object):
    def __init__(self, layer, location_type, source='UNKNOWN', filter_bounds=False, verbose=False):
        self.layer = layer
        metro = get_metro()
        self.metro_name = metro['metro_name'].upper()
        self.now = datetime.datetime.now()
        if isinstance(location_type, int):
            location_type = LocationType.objects.get(id=location_type)
        self.location_type = location_type
        self.source = source
        self.filter_bounds = filter_bounds
        self.verbose = verbose
        if self.filter_bounds:
            from ebpub.utils.geodjango import get_default_bounds
            self.bounds = get_default_bounds()

    def create_location(self, name, location_type, geom, display_order=0):
        source = self.source
        geom = geos_with_projection(geom, 4326)
        geom = ensure_valid(geom, name)
        geom = flatten_geomcollection(geom)
        if not isinstance(location_type, int):
            location_type = location_type.id
        kwargs = dict(
            name=name,
            slug=slugify(name),
            location=geom,
            location_type_id=location_type,
            city=self.metro_name,
            source=source,
            is_public=True,
        )
        if not self.should_create_location(kwargs):
            return
        kwargs['defaults'] = {
            'creation_date': self.now,
            'last_mod_date': self.now,
            'display_order': display_order,
            'normalized_name': normalize(name),
            'area': geom.transform(3395, True).area,
            }
        try:
            loc, created = Location.objects.get_or_create(**kwargs)
        except IntegrityError:
            # Usually this means two towns with the same slug.
            # Try to fix that.
            slug = kwargs['slug']
            existing = Location.objects.filter(slug=slug).count()
            if existing:
                slug = slugify('%s-%s' % (slug, existing + 1))
                logger.info("Munged slug %s to %s to make it unique" % (kwargs['slug'], slug))
                kwargs['slug'] = slug
                loc, created = Location.objects.get_or_create(**kwargs)
            else:
                raise

        logger.info('%s %s %s' % (created and 'Created' or 'Already had', self.location_type.name, loc))
        logger.info('Populating newsitem locations ... ')
        populate_ni_loc(loc)
        logger.info('done.\n')

        return created

    def save(self, name_field):
        num_created = 0
        num_updated = 0
        features = sorted(self.layer, key = lambda f: f.get(name_field))
        for i, feature in enumerate(features):
            name = feature.get(name_field)
            location_type = self.get_location_type(feature)
            created = self.create_location(name, location_type, feature.geom, display_order=i)
            if created:
                num_created += 1
            else:
                num_updated += 1

        return (num_created, num_updated)

    def should_create_location(self, fields):
        if self.filter_bounds:
            if not fields['location'].intersects(self.bounds):
                logger.info("Skipping %s, out of bounds" % fields['name'])
                return False
        return True

    def get_location_type(self, feature):
        return self.location_type

optparser = OptionParser(usage= 'usage: %prog [options] type_slug /path/to/shapefile')
optparser.add_option('-n', '--name-field', dest='name_field', default='name', help='field that contains location\'s name')
optparser.add_option('-i', '--layer-index', dest='layer_id', default=0, help='index of layer in shapefile')
optparser.add_option('-s', '--source', dest='source', default='UNKNOWN', help='source metadata of the shapefile')
optparser.add_option('-v', '--verbose',  action='store_true', default=False, help='be verbose')
optparser.add_option('-b', '--filter-bounds', action='store_true', default=False,
                     help="exclude locations not within the lon/lat bounds of "
                     " your metro's extent (from your settings.py) (default false)")

def get_or_create_location_type(slug, name, name_plural, verbose):
    metro = get_metro()
    metro_name = metro['metro_name'].upper()
    try:
        location_type = LocationType.objects.get(slug = slug)
        logger.info("Location type %s already exists, ignoring type-name and type-name-plural" % slug)
    except LocationType.DoesNotExist:
        location_type, _ = LocationType.objects.get_or_create(
            name = name,
            plural_name = name_plural,
            scope = metro_name,
            slug = slug,
            is_browsable = True,
            is_significant = True,
            )
    return location_type

def layer_from_shapefile(path, layer_id):
    if not os.path.exists(path):
        raise ValueError('file does not exist: ' + path)
    ds = DataSource(path)
    return ds[layer_id]

def parse_args(optparser, argv):
    # Add some options that aren't relevant to scripts that import our optparser.
    optparser.add_option('--type-name', dest='type_name', default='', help='specifies the location type name')
    optparser.add_option('--type-name-plural', dest='type_name_plural', default='', help='specifies the location type plural name')
    opts, args = optparser.parse_args(argv)

    if len(args) != 2:
        optparser.error('must supply type slug and path to shapefile')
    type_slug = args[0]

    try:
        layer = layer_from_shapefile(args[1], opts.layer_id)
    except ValueError as e:
        optparser.error(str(e))

    return type_slug, layer, opts

def main():
    type_slug, layer, opts = parse_args(optparser, sys.argv[1:])
    if not opts.verbose:
        logging.basicConfig()
        logger.setLevel(logging.WARN)

    location_type = get_or_create_location_type(type_slug, opts.type_name, opts.type_name_plural, opts.verbose)

    importer = LocationImporter(
        layer,
        location_type,
        opts.source,
        opts.filter_bounds,
        opts.verbose
    )
    num_created, num_updated = importer.save(opts.name_field)

    logger.info('Created %s, updated %s %s.' % (num_created, num_updated, location_type.plural_name))

if __name__ == '__main__':
    sys.exit(main())

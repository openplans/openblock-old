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

import sys
import optparse
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.gdal.error import OGRIndexError
from ebdata.parsing import dbf
from ebpub.streets.blockimport.base import BlockImporter

STATE_FIPS = {
    '02': ('AK', 'ALASKA'),
    '01': ('AL', 'ALABAMA'),
    '05': ('AR', 'ARKANSAS'),
    '60': ('AS', 'AMERICAN SAMOA'),
    '04': ('AZ', 'ARIZONA'),
    '06': ('CA', 'CALIFORNIA'),
    '08': ('CO', 'COLORADO'),
    '09': ('CT', 'CONNECTICUT'),
    '11': ('DC', 'DISTRICT OF COLUMBIA'),
    '10': ('DE', 'DELAWARE'),
    '12': ('FL', 'FLORIDA'),
    '13': ('GA', 'GEORGIA'),
    '66': ('GU', 'GUAM'),
    '15': ('HI', 'HAWAII'),
    '19': ('IA', 'IOWA'),
    '16': ('ID', 'IDAHO'),
    '17': ('IL', 'ILLINOIS'),
    '18': ('IN', 'INDIANA'),
    '20': ('KS', 'KANSAS'),
    '21': ('KY', 'KENTUCKY'),
    '22': ('LA', 'LOUISIANA'),
    '25': ('MA', 'MASSACHUSETTS'),
    '24': ('MD', 'MARYLAND'),
    '23': ('ME', 'MAINE'),
    '26': ('MI', 'MICHIGAN'),
    '27': ('MN', 'MINNESOTA'),
    '29': ('MO', 'MISSOURI'),
    '28': ('MS', 'MISSISSIPPI'),
    '30': ('MT', 'MONTANA'),
    '37': ('NC', 'NORTH CAROLINA'),
    '38': ('ND', 'NORTH DAKOTA'),
    '31': ('NE', 'NEBRASKA'),
    '33': ('NH', 'NEW HAMPSHIRE'),
    '34': ('NJ', 'NEW JERSEY'),
    '35': ('NM', 'NEW MEXICO'),
    '32': ('NV', 'NEVADA'),
    '36': ('NY', 'NEW YORK'),
    '39': ('OH', 'OHIO'),
    '40': ('OK', 'OKLAHOMA'),
    '41': ('OR', 'OREGON'),
    '42': ('PA', 'PENNSYLVANIA'),
    '72': ('PR', 'PUERTO RICO'),
    '44': ('RI', 'RHODE ISLAND'),
    '45': ('SC', 'SOUTH CAROLINA'),
    '46': ('SD', 'SOUTH DAKOTA'),
    '47': ('TN', 'TENNESSEE'),
    '48': ('TX', 'TEXAS'),
    '49': ('UT', 'UTAH'),
    '51': ('VA', 'VIRGINIA'),
    '78': ('VI', 'VIRGIN ISLANDS'),
    '50': ('VT', 'VERMONT'),
    '53': ('WA', 'WASHINGTON'),
    '55': ('WI', 'WISCONSIN'),
    '54': ('WV', 'WEST VIRGINIA'),
    '56': ('WY', 'WYOMING'),
}

# Only import features with these MTFCC codes - primary road,
# secondary road, and city street
VALID_MTFCC = set(['S1100', 'S1200', 'S1400'])

# There's a few of these that have FULLNAME and may even have addresses.
VALID_MTFCC.add('S1730') # alley, often unnamed.
VALID_MTFCC.add('S1640') # service roads, may have buildings.
VALID_MTFCC.add('S1740') # private roads, often unnamed.

class TigerImporter(BlockImporter):
    """
    Imports blocks using TIGER/Line data from the US Census.

    If `filter_city` is passed, we will skip features which don't have
    at least one of left_city or right_city matching the string.

    If `filter_bounds` is passed, it will be treated as an OGR geometry
    to use for filtering out features outside the geometry.

    `edges_shp` contains all the feature edges (i.e. street segment
    geometries); `featnames_dbf` contains metadata; `faces_dbf` and
    `place_shp` contain information about cities and states.

    Note this importer requires a lot of memory, because it loads the
    necessary .DBF files into memory for various lookups.

    Please refer to Census TIGER/Line shapefile documentation
    regarding the relationships between shapefiles and support DBF
    databases:

    http://www.census.gov/geo/www/tiger/tgrshp2008/rel_file_desc_2008.txt
    """
    def __init__(self, edges_shp, featnames_dbf, faces_dbf, place_shp,
                 filter_city=None, filter_bounds=None, filter_locations=(),
                 verbose=False, encoding='utf8', fix_cities=False):
        BlockImporter.__init__(self, shapefile=edges_shp, layer_id=0,
                               verbose=verbose, encoding=encoding)
        self.fix_cities = fix_cities
        self.featnames_db = featnames_db = {}
        for tlid, row in self._load_rel_db(featnames_dbf, 'TLID').iteritems():
            # TLID is Tiger/Line ID, unique per edge.
            # We use TLID instead of LINEARID as the key because
            # LINEARID is only unique per 'linear feature', which is
            # an implicit union of some edges. So if we used LINEARID,
            # we'd clobber a lot of keys in the call to
            # _load_rel_db().
            # Fixes #14 ("missing blocks").
            if row['MTFCC'] not in VALID_MTFCC:
                continue
            if not row.get('FULLNAME'):
                self.log("skipping tlid %r, no fullname" % tlid)
                continue

            featnames_db.setdefault(tlid, [])
            featnames_db[tlid].append(row)

        self.faces_db = self._load_rel_db(faces_dbf, 'TFID')
        # Load places keyed by FIPS code
        places_layer = DataSource(place_shp)[0]
        fields = places_layer.fields
        self.places = places = {}
        for feature in places_layer:
            try:
                fips = feature.get('PLACEFP10')  # 2010 Census files.
            except OGRIndexError:
                fips = feature.get('PLACEFP')  # Older Census files.
            values = dict(zip(fields, map(feature.get, fields)))
            places[fips] = values
        self.filter_city = filter_city and filter_city.upper() or None
        if hasattr(filter_bounds, 'ogr'):
            filter_bounds = filter_bounds.ogr
        self.filter_bounds = filter_bounds
        self.tlids_with_blocks = set()


    def _load_rel_db(self, dbf_file, rel_key):
        """
        Reads rows as dicts from a .dbf file.
        Returns a mapping of rel_key -> row dict.
        """
        f = open(dbf_file, 'rb')
        db = {}
        rowcount = 0
        try:
            for row in dbf.dict_reader(f, strip_values=True):
                db[row[rel_key]] = row
                rowcount += 1
                self.log(
                    " GOT DBF ROW %s for %s" % (row[rel_key], row.get('FULLNAME', 'unknown')))
        finally:
            f.close()
        self.log("Rows in %s: %d" % (dbf_file, rowcount))
        self.log("Unique keys for %r: %d" % (rel_key, len(db)))
        return db

    def _get_city(self, feature, side):
        city = ''
        if self.fix_cities:
            from ebpub.db.models import get_city_locations
            overlapping_cities = list(get_city_locations().filter(location__intersects=feature.geom.geos))
            if overlapping_cities:
                city = overlapping_cities[0].name
                if self.verbose:
                    print >> sys.stderr, "overriding city to %s" % city
        else:
            fid = feature.get('TFID' + side)
            if fid in self.faces_db:
                face = self.faces_db[fid]
                # Handle both 2010 and older census files.
                pid = face.get('PLACEFP10') or face['PLACEFP']
                if pid in self.places:
                    place = self.places[pid]
                    # Handle both 2010 and earlier Census files.
                    city = place.get('NAME10') or place['NAME']
        return city

    def _get_state(self, feature, side):
        fid = feature.get('TFID' + side)
        if fid in self.faces_db:
            face = self.faces_db[fid]
            # Handle both 2010 and older census files.
            state_fip = STATE_FIPS[face.get('STATEFP10') or face['STATEFP']]
            return state_fip[0]
        else:
            return ''

    def skip_feature(self, feature):
        if self.filter_bounds:
            if not feature.geom.intersects(self.filter_bounds):
                if self.verbose:
                    print >> sys.stderr, "Skipping %s, out of bounds" % feature
                return True

        if not feature.get('MTFCC') in VALID_MTFCC:
            if self.verbose:
                print >> sys.stderr, "Skipping %s, not a valid feature type" % feature.get('MTFCC')
            return True

        if self.filter_city:
            in_city = False
            for side in ('R', 'L'):
                if self._get_city(feature, side).upper() == self.filter_city:
                    in_city = True
            if not in_city:
                if self.verbose:
                    print >> sys.stderr, "Skipping %s, out of city" % feature
                return True

        if not (
            ((feature.get('RFROMADD') and feature.get('RTOADD')) or
            (feature.get('LFROMADD') and feature.get('LTOADD')))):
            if self.verbose:
                print >> sys.stderr, "Skipping %s, not enough address info" % feature
            return True

        return False

    def gen_blocks(self, feature):
        block_fields = {}
        tlid = feature.get('TLID')
        for field_key, feature_key in (('right_from_num', 'RFROMADD'),
                                       ('left_from_num', 'LFROMADD'),
                                       ('right_to_num', 'RTOADD'),
                                       ('left_to_num', 'LTOADD')):
            block_fields[field_key] = feature.get(feature_key)

        block_fields['right_zip'] = feature.get('ZIPR')
        block_fields['left_zip'] = feature.get('ZIPL')
        for side in ('right', 'left'):
            block_fields[side + '_city'] = self._get_city(feature, side[0].upper()).upper()
            block_fields[side + '_state'] = self._get_state(feature, side[0].upper()).upper()

        if tlid in self.featnames_db:
            for featname in self.featnames_db[tlid]:
                block_fields['street'] = featname['NAME'].upper()
                block_fields['predir'] = featname['PREDIRABRV'].upper()
                block_fields['suffix'] = featname['SUFTYPABRV'].upper()
                block_fields['postdir'] = featname['SUFDIRABRV'].upper()
                yield block_fields.copy()

                self.tlids_with_blocks.add(tlid)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = optparse.OptionParser(usage='%prog edges.shp featnames.dbf faces.dbf place.shp')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
    parser.add_option('-c', '--city', dest='city', help='A city name to filter against')
    parser.add_option('-f', '--fix-cities', action="store_true", default=False,
                      help='Whether to override "city" attribute of blocks and '
                      'streets by finding an intersecting Location of a city-ish '
                      'type. Only makes sense if you have configured '
                      'multiple_cities=True in the METRO_LIST of your settings.py, '
                      'and after you have created some appropriate Locations.')

    parser.add_option('-b', '--filter-bounds', action="store", default=1,
                      type='int',
                      help='Whether to skip blocks outside the metro extent from your '
                      'settings.py. Default 1 (true); use 0 to disable.')
    parser.add_option('-l', '--filter-location', action="append",
                      help='A location (spelled as location-type-slug:location-slug) '
                      'that will be used to filter out blocks outside its boundaries. '
                      'May be passed more than once.'
                      )

    parser.add_option('-e', '--encoding', dest='encoding',
                      help='Encoding to use when reading the shapefile',
                      default='utf8')
    (options, args) = parser.parse_args(argv)
    if len(args) != 4:
        return parser.error('must provide 4 arguments, see usage')

    if options.filter_bounds:
        from ebpub.utils.geodjango import get_default_bounds
        filter_bounds = get_default_bounds()
    else:
        filter_bounds = None

    # Optionally filter on bounds of some Locations too.
    loc_bounds = None
    for locslug in options.filter_location or []:
        typeslug, locslug = locslug.split(':', 1)
        from ebpub.db.models import Location
        location = Location.objects.get(location_type__slug=typeslug, slug=locslug)
        if loc_bounds is None:
            loc_bounds = location.location
        else:
            loc_bounds = loc_bounds.union(location.location)

    if None not in (filter_bounds, loc_bounds):
        filter_bounds = filter_bounds.intersection(loc_bounds)
    elif loc_bounds is not None:
        filter_bounds = loc_bounds
    else:
        filter_bounds = filter_bounds

    tiger = TigerImporter(*args, verbose=options.verbose,
                           filter_city=options.city, 
                           filter_bounds=filter_bounds,
                           encoding=options.encoding,
                           fix_cities=options.fix_cities)
    num_created = tiger.save()
    print "Created %d blocks" % num_created
    if options.verbose:
        print "... from %d feature names" % len(tiger.featnames_db)
        print "feature tlids with blocks: %d" % len(tiger.tlids_with_blocks)
        print
        import pprint
        tlids_wo_blocks = set(tiger.featnames_db.keys()).difference(tiger.tlids_with_blocks)
        print "feature tlids WITHOUT blocks: %d" % len(tlids_wo_blocks)
        all_rows = []
        for t in tlids_wo_blocks:
            all_rows.extend(tiger.featnames_db[t])
        print "Rows: %d" % len(all_rows)
        names = [(r['FULLNAME'], r['TLID']) for r in all_rows]
        names.sort()
        print "================="
        for n, t in names:
            print n, t
        for tlid in sorted(tlids_wo_blocks)[:10]:
            feat = tiger.featnames_db[tlid]
            pprint.pprint(feat)


if __name__ == '__main__':
    sys.exit(main())

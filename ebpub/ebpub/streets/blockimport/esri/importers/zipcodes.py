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
import sys

class EsriImporter(object):
    def __init__(self, shapefile, city, layer_id=0):
        ds = DataSource(shapefile)
        self.layer = ds[layer_id]
        self.city = city
        self.location_type, _ = LocationType.objects.get_or_create(
            name = 'ZIP Code',
            plural_name = 'ZIP Codes',
            scope = 'U.S.A.',
            slug = 'zipcodes',
            is_browsable = True,
            is_significant = True,
        )

    def save(self, verbose=False):
        # The ESRI ZIP Code layer breaks ZIP Codes up along county
        # boundaries, so we need to collapse them first before
        # proceeding
        zipcodes = {}
        for feature in self.layer:
            zipcode = feature.get('POSTAL')
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
            zipcode_obj, created = Location.objects.get_or_create(
                name = zipcode,
                normalized_name = zipcode,
                slug = zipcode,
                location_type = self.location_type,
                location = geom,
                display_order = i,
                city = self.city,
                source = 'ESRI',
                area = geom.transform(3395, True).area,
                is_public = True,
                creation_date = now,
                last_mod_date = now,
            )
            if created:
                num_created += 1
            if verbose:
                print >> sys.stderr, '%s ZIP Code %s ' % (created and 'Created' or 'Already had', zipcode_obj.name)
        return num_created


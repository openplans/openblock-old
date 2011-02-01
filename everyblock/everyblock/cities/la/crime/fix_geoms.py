#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of everyblock
#
#   everyblock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   everyblock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with everyblock.  If not, see <http://www.gnu.org/licenses/>.
#

from ebdata.retrieval.utils import locations_are_close
from ebpub.db.models import NewsItem
from ebpub.geocoder import SmartGeocoder, ParsingError, GeocodingException
from django.contrib.gis.geos import Point

geocoder = SmartGeocoder()
THRESHOLD = 375

def fix_crime_geom():
    qs = NewsItem.objects.filter(schema__slug='crime', location__isnull=False)
    count = qs.count()
    for i, ni in enumerate(qs.iterator()):
        print '# => Checking %s of %s' % (i, count)
        x, y = [float(n) for n in ni.attributes['xy'].split(';')]
        pt = Point((x, y))
        pt.srid = 4326
        location_name = ni.location_name.replace('XX', '01')
        try:
            result = geocoder.geocode(location_name)
        except (GeocodingException, ParsingError):
            print '     Could not geocode'
            NewsItem.objects.filter(id=ni.id).update(location=None)
        else:
            is_close, distance = locations_are_close(ni.location, pt, THRESHOLD)
            if not is_close:
                print '     Too far: %s' % distance
                NewsItem.objects.filter(id=ni.id).update(location=None)
            else:
                print '     Fine'

if __name__ == "__main__":
    fix_crime_geom()

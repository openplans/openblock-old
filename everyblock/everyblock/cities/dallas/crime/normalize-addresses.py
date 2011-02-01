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

from ebpub.db.models import NewsItem
from retrieval import StreetNormalizer # relative import

def normalize():
    normalizer = StreetNormalizer()
    for ni in NewsItem.objects.filter(schema__slug='crime-reports').iterator():
        block, direction, street = ni.attributes['street'].split(';')
        record = {
            'offensestreet': street,
            'offenseblock': block,
            'offensedirection': direction,
        }
        normalized_address = normalizer.normalize_address(record)
        if ni.location_name != normalized_address:
            ni.location_name = normalized_address
            ni.save()
            print ni.attributes['street']
            print normalized_address
    normalizer.print_stats()

if __name__ == "__main__":
    normalize()

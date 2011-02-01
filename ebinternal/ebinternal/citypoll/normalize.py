#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebinternal
#
#   ebinternal is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebinternal is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebinternal.  If not, see <http://www.gnu.org/licenses/>.
#

from ebinternal.citypoll.models import Vote

def normalize_cities():
    total = 0
    for v in Vote.objects.distinct().filter(city__id__isnull=False).values('city_text', 'city'):
        total += Vote.objects.filter(city__id__isnull=True, city_text__iexact=v['city_text']).update(city=v['city'])
    return total

if __name__ == "__main__":
    print normalize_cities()

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
from ebpub.db.models import Location

def alphabetize_locations(location_type_slug=None):
    if location_type_slug is None:
        sys.stderr.write("using default slug 'neighborhoods'")
        location_type_slug = 'neighborhoods'
    for i, loc in enumerate(Location.objects.filter(location_type__slug=location_type_slug).order_by('name').iterator()):
        print loc.name
        loc.display_order = i
        loc.save()

def main():
    location_type_slug = len(sys.argv[1:]) and sys.argv[1] or None
    sys.exit(alphabetize_locations(location_type_slug))

if __name__ == "__main__":
    main()


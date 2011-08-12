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
from ebpub.geocoder.parser.parsing import normalize
from ebpub.streets.models import Suburb

def populate_suburbs(suburb_list):
    for suburb in suburb_list:
        Suburb.objects.create(name=suburb, normalized_name=normalize(suburb))

def main():
    import sys
    import os
    if (not len(sys.argv) > 1) or (not os.path.exists(sys.argv[1])):
        sys.stderr.write("Usage: %s FILE\n\n" % sys.argv[0])
        sys.stderr.write("The file should be a text file with one suburb name per line.\n")
        sys.stderr.write("For openblock's purposes, a 'suburb' is just a\n"
                         "nearby city that we don't care about importing.\n")

        sys.exit(1)
    suburb_list = [line for line in open(sys.argv[1], 'r').read().split('\n') if line]
    populate_suburbs(suburb_list)

if __name__ == "__main__":
    sys.exit(main())

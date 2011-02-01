#!/usr/bin/env python
#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#


if __name__ == '__main__':
    import sys
    import virtualenv

    if len(sys.argv) < 3: 
        print 'usage: %s <in> <out>'
        sys.exit(0)

    in_file = sys.argv[1]
    out_file = sys.argv[2]

    extras = open(in_file).read()
    output = virtualenv.create_bootstrap_script(open(in_file).read())
    f = open(out_file, 'w').write(output)

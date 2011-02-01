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

from ebpub.streets.name_utils import make_pretty_name
from ebpub.streets.models import Block

def update_block_pretty_names():
    for b in Block.objects.all():
        name = make_pretty_name(b.left_from_num, b.left_to_num, 
                                b.right_from_num, b.right_to_num,
                                b.predir, b.street, b.suffix, b.postdir)[1]
        if name != b.pretty_name:
            print 'Pretty name: %s -- from: %s' % (b.pretty_name, name)
            b.pretty_name = name
            b.save()

if __name__ == "__main__":
    update_block_pretty_names()




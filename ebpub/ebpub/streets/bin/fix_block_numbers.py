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

from ebpub.streets.name_utils import make_block_numbers
from ebpub.streets.models import Block


def update_all_block_numbers(verbose=False):
    """Derives from_num and to_num from left_from_num, etc.
    """
    for b in Block.objects.all():
        (from_num, to_num) = make_block_numbers(
            b.left_from_num, b.left_to_num, b.right_from_num, b.right_to_num)
        if b.from_num != from_num or b.to_num != to_num:
            b.from_num = from_num
            b.to_num = to_num
            b.full_clean()
            b.save()
            if verbose:
                print "Updating numbers for %s to %s-%s" % (b, from_num, to_num)

def main():
    update_all_block_numbers(verbose=True)

if __name__ == "__main__":
    main()


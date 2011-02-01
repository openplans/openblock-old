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

from django.conf import settings
from ebpub.streets.models import Block


def delete_blocks_outside_city(verbose=False):
    """Derives from_num and to_num from left_from_num, etc.
    """
    not_in_city = Block.objects.exclude(right_city=settings.SHORT_NAME.upper()).exclude(left_city=settings.SHORT_NAME.upper())
    if verbose:
        print "Deleting %d blocks outside the city" % not_in_city.count()
    not_in_city.delete()


if __name__ == "__main__":
    delete_blocks_outside_city(verbose=True)

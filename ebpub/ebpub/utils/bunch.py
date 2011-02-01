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

import math

# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/425044
def bunch(lst, size):
    size = int(size)
    return [lst[i:i+size] for i in range(0, len(lst), size)]

def bunchlong(lst, size):
    size = float(int(size))
    return bunch(lst, int(math.ceil(len(lst) / size)))

def stride(lst, size):
    """
    >>> stride([1, 2, 3, 4, 5, 6], 2)
    [[1, 3, 5], [2, 4, 6]]
    >>> stride([1, 2, 3, 4, 5], 2)
    [[1, 3, 5], [2, 4]]
    >>> stride([1, 2, 3, 4, 5], 1)
    [[1, 2, 3, 4, 5]]
    >>> stride([1, 2, 3, 4, 5, 6], 3)
    [[1, 4], [2, 5], [3, 6]]
    >>> stride([1, 2, 3, 4, 5, 6, 7], 3)
    [[1, 4, 7], [2, 5], [3, 6]]
    """
    size = int(size)
    return [lst[i::size] for i in range(size)]

if __name__ == "__main__":
    import doctest
    doctest.testmod()

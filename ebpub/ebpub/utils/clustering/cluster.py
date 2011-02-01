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

"""
Map marker clustering

We need to know:

    + List of points (in lat/lng)

    + List of map resolutions

    + Size of buffer, and how to translate it into lat/lng
"""

import math
from bunch import Bunch # relative import

def euclidean_distance(a, b):
    """
    Calculates the Euclidean distance between two points.

    Assumes (x, y) pairs.
    """
    return math.hypot(a[0] - b[0], a[1] - b[1])

def buffer_cluster(objects, radius, dist_fn=euclidean_distance):
    """
    Clusters objects into bunches within a buffer by a given radius.

    Differs from k-means clustering in that the number of bunches is
    not known before the program is run or given as an argument: a
    "natural" number of bunches is returned, depending on whether a
    point falls within a buffer. The number of bunches is inversely
    proportional to the size of the buffer: the larger the buffer,
    the fewer number of bunches (but the larger the number of points
    contained in each bunch).

    Similar to k-means clustering in that it calculates a new center
    point for each bunch on each iteration, eventually arriving at
    a steady state.

    I'm just calling it 'buffer clustering': this may be called
    something else for real and there may be a better implementation,
    but I don't know better!

    ``objects`` is a dict with keys for ID some domain object, and 
    the values being 2-tuples representing their points on a 
    coordinate system.
    """
    bunches = []
    buffer = radius
    for key, point in objects.iteritems():
        point_is_bunched = False
        for bunch in bunches:
            if dist_fn(point, bunch.center) <= buffer:
                bunch.add_obj(key, point)
                point_is_bunched = True
                break
        if not point_is_bunched:
            bunches.append(Bunch(key, point))
    return bunches

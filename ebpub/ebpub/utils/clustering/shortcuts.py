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

from ebpub.utils import clustering

def cluster_newsitems(qs, radius=26):
    """
    A convenience function for clustering a newsitem queryset.

    Returns: a mapping of scale -> list of clusters for that scale.
    """
    return clustering.cluster_scales(
        dict([(ni.id, (ni.location.centroid.x, ni.location.centroid.y))
              for ni in qs if ni.location]),
        radius)

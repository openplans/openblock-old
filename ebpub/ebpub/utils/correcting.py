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

class InvalidGeometry(Exception):
    pass

def correcting_layer(layer):
    """
    Generator for correcting invalid geometries of the layer's
    features. Yields 2-tuples (feature, geometry), where geometry is
    the corrected geometry. The original feature.geom is left
    preserved.

    Usage is simply to wrap an existing gdal.layer.Layer with this
    function and iterate over features.
    """
    for feature in layer:
        geom = feature.geom
        if not geom.geos.valid:
            # Note that the correction method is to buffer the
            # geometry with distance 0 -- this may not always work, so
            # check the resulting geometry before reassigning the
            # feature's geometry
            new_geom = geom.geos.buffer(0.0)
            if new_geom.valid:
                geom = new_geom.ogr
            else:
                raise InvalidGeometry()
        yield (feature, geom)

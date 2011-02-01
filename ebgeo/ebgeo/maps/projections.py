#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebgeo
#
#   ebgeo is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebgeo is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebgeo.  If not, see <http://www.gnu.org/licenses/>.
#

'''
Definitions and utilities for projection support.

TODO: GeoDjango provides much more robust tools for setting up projection
objects from EPSG codes, PROJ4 and WKT, etc. In the long run we should use that
intead.
'''

EPSG_PROJ4 = {
    4326: '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
    # spherical mercator
    900913: '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 ' \
            '+x_0=0.0 +y_0=0 +k=1.0 +units=m ' \
            '+nadgrids=@null +no_defs',
    # USA_Contiguous_Albers_Equal_Area_Conic
    # cf. http://spatialreference.org/ref/epsg/102003/
    102003: '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 ' \
            '+y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs'
}

def epsg_to_proj4(code):
    if code.lower().startswith('epsg:'):
        code = code.split(':')[1]
    return EPSG_PROJ4[int(code)]

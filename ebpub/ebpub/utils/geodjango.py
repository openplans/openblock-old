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
Utility functions for working with GeoDjango GDAL and GEOS data


"""

from django.contrib.gis import geos
from django.contrib.gis.geos import Point, LineString, Polygon, GeometryCollection, MultiPoint, MultiLineString, MultiPolygon
from ebpub.metros.allmetros import get_metro
import logging

logger = logging.getLogger('ebpub.utils.geodjango')

def reduce_layer_geom(layer, method):
    """
    Iterates over all the geometries in an GDAL layer and successively
    applies given ``method`` to the geometries.
    """
    def reduction(x, y):
        return getattr(x, method)(y)
    
    return reduce(reduction, [feat.geom for feat in layer])

# TODO: remove this once line_merge is added to django.contrib.gis.geos
from django.contrib.gis.geos.libgeos import lgeos
from django.contrib.gis.geos.prototypes.topology import topology
geos_linemerge = topology(lgeos.GEOSLineMerge)
def line_merge(geom):
    return geom._topology(geos_linemerge(geom.ptr))

def flatten(geos_geom):
    """
    Flattens a GEOS geometry and returns a list of the component geometries.
    """
    def _flatten(geom, acc):
        if isinstance(geom, (Point, LineString, Polygon)):
            acc.append(geom)
            return acc
        elif isinstance(geom, (GeometryCollection, MultiPoint, MultiLineString, MultiPolygon)):
            subgeom_list = list(geom)
            if subgeom_list:
                acc.append(subgeom_list.pop(0))
                for subgeom in subgeom_list:
                    _flatten(subgeom, acc)
            return acc
        else:
            raise TypeError, 'not a recognized GEOSGeometry type'
    flattened = []
    _flatten(geos_geom, flattened)
    return flattened

def make_geomcoll(geom_list):
    """
    From a list of geometries, return a single GeometryCollection (or
    subclass) geometry.

    This flattens multi-point/linestring/polygon geometries in the
    list.
    """
    flattened = []

    for geom in geom_list:
        flattened.extend(flatten(geom))

    return GeometryCollection(flattened)

def make_multi(geom_list, collapse_single=False):
    """
    Convert a list of Geometries (of the same type) into a single
    Multi(Point|Linestring|Polygon).
    """
    if len(geom_list) == 1 and collapse_single:
        return geom_list[0]

    geom_types = set(g.geom_type for g in geom_list)

    if len(geom_types) > 1:
        raise ValueError, 'all geometries must be of the same geom_type'

    geom_type = geom_types.pop()

    valid_geom_types = ('Point', 'LineString', 'Polygon')

    if geom_type not in valid_geom_types:
        raise ValueError, 'geometries must be of type %s' % ', '.join(valid_geom_types)

    cls = getattr(geos, 'Multi%s' % geom_type)
    return cls(geom_list)


def flatten_geomcollection(geom):
    """
    Workaround for bug #95: if we get a GeometryCollection,
    save it instead as a MultiPolygon, because PostGIS doesn't support
    using Collections for anything useful like
    ST_Intersects(some_other_geometry), so we effectively can't
    use them at all. Yuck.
    """
    if geom.geom_type == 'GeometryCollection':
        geom = make_multi(flatten(geom))
        logger.warn("Got a GeometryCollection. Can't call ST_Intersects() on those."
                    " Munged it into a %s." % geom.geom_type)
    return geom

def smart_transform(geom, srid, clone=True):
    """
    Returns a new geometry transformed to the srid given. Assumes if
    the initial geom is lacking an SRS that it is EPSG 4326. (Hence the
    "smartness" of this function.) This fixes many silent bugs when
    transforming between SRSes when the geometry is missing this info.
    """
    if not geom.srs:
        geom.srid = 4326
    return geom.transform(srid, clone=clone)


def ensure_valid(geom, name=''):
    """Make sure a geometry is valid; if necessary, make a 0.0 buffer
    around it. (This is a well-known hack to fix broken geometries.)
    """
    if not geom.valid:
        geom = geom.buffer(0.0)
        if not geom.valid:
            logger.warn('invalid geometry for %s' % name)
    return geom

def intersects_metro_bbox(geom):
    """
    Return True if the geometry intersects with the bounding box of
    the current metro.
    """
    return geom.intersects(get_default_bounds())


def get_default_bounds():
    """Returns the bounding box of the metro, as a Polygon.

    >>> import mock
    >>> metrodict = {'extent': (-10.0, 15.0, -5.0, 20.0)}
    >>> with mock.patch('ebpub.utils.geodjango.get_metro', lambda: metrodict) as get_metro:
    ...     bounds = get_default_bounds()
    >>> bounds  #doctest: +ELLIPSIS
    <Polygon object at ...>
    >>> bounds.extent
    (-10.0, 15.0, -5.0, 20.0)
    """
    return Polygon.from_bbox(get_metro()['extent'])

def interpolate(linestring, distance, normalized=True):
    """
    Find a point along the linestring that is ``distance`` from the first point.

    If normalized=True, distance is fraction of the linestring's length
    (range 0.0 - 1.0).

    Example:

    >>> ls = LineString((0.0, 0.0), (1.1, 1.1), (2.2, 2.2))
    >>> interpolate(ls, 0, True).coords
    (0.0, 0.0)
    >>> interpolate(ls, 0.5, True).coords
    (1.1, 1.1)
    >>> interpolate(ls, 1.0, True).coords
    (2.2, 2.2)
    """
    # Use Shapely because geodjango's native GEOS support doesn't
    # provide the interpolate() function.
    # See https://code.djangoproject.com/ticket/18209
    import shapely.geometry
    try:
        center = shapely.geometry.LineString(linestring).interpolate(distance, normalized)
    except (ImportError, AttributeError):
        # Might be that the platform doesn't have a recent-enough GEOS; needs 1.6.
        # This version uses database, and requires normalized.
        if not normalized:
            raise ValueError("Can't call interpolate() with normalized=False unless you have GEOS version 1.6 or later.")
        from django.db import connection
        from django.contrib.gis.geos import fromstr
        cursor = connection.cursor()
        cursor.execute('SELECT line_interpolate_point(%s, %s)', [linestring.wkt, distance])
        wkb_hex = cursor.fetchone()[0]
        center = fromstr(wkb_hex)
    center = Point(*list(center.coords))
    return center


def geos_with_projection(geom, projection=4326):
    """
    Returns a GEOSGeometry with the projection set.

    ``geom`` can be a GEOSGeometry or OGRGeometry or subclass.

    ``projection`` can be an integer SRID or a SpatialReference object.
    Default projection is 4326 (aka WGS 84).


    You can use a GEOSGeometry with no projection::

      >>> from django.contrib.gis.geos import Point, GEOSGeometry
      >>> from django.contrib.gis.gdal import OGRGeometry, SpatialReference
      >>>
      >>> geos_no_srid = Point((1.0, 2.0))
      >>> print geos_no_srid.srid
      None
      >>> geom = geos_with_projection(geos_no_srid)
      >>> geom.srid
      4326
      >>> geom.x, geom.y
      (1.0, 2.0)

    You can use a GEOSGeometry with a projection::

      >>> geos_with_srid = Point((1.0, 2.0), srid=4326)
      >>> geos_with_srid.srid
      4326
      >>> geom = geos_with_projection(geos_with_srid)
      >>> geom.srid
      4326
      >>> geom.x, geom.y
      (1.0, 2.0)


   YOu can use an OGRGeometry with no projection::

      >>> ogr_no_srs = OGRGeometry('POINT (1 2)')
      >>> print ogr_no_srs.srs
      None
      >>> geom = geos_with_projection(ogr_no_srs)
      >>> print geom.srid
      4326
      >>> geom.x, geom.y
      (1.0, 2.0)

   You can use an OGR geometry with a projection that has no srid,
   there are some like that::

      >>> test_srs = SpatialReference(
      ...     '''PROJCS["NAD_1983_StatePlane_North_Carolina_FIPS_3200_Feet",
      ...     GEOGCS["GCS_North_American_1983",
      ...         DATUM["North_American_Datum_1983",
      ...             SPHEROID["GRS_1980",6378137.0,298.257222101]],
      ...         PRIMEM["Greenwich",0.0],
      ...         UNIT["Degree",0.0174532925199433]],
      ...     PROJECTION["Lambert_Conformal_Conic_2SP"],
      ...     PARAMETER["False_Easting",2000000.002616666],
      ...     PARAMETER["False_Northing",0.0],
      ...     PARAMETER["Central_Meridian",-79.0],
      ...     PARAMETER["Standard_Parallel_1",34.33333333333334],
      ...     PARAMETER["Standard_Parallel_2",36.16666666666666],
      ...     PARAMETER["Latitude_Of_Origin",33.75],
      ...     UNIT["Foot_US",0.3048006096012192]]
      ... '''
      ...     )
      >>> ogr_with_srs_but_no_srid = OGRGeometry('POINT (1 2)', srs=4326)
      >>> ogr_with_srs_but_no_srid.transform(test_srs)
      >>> print ogr_with_srs_but_no_srid.srs.name
      NAD_1983_StatePlane_North_Carolina_FIPS_3200_Feet
      >>> print ogr_with_srs_but_no_srid.srid
      None
      >>> geom = geos_with_projection(ogr_with_srs_but_no_srid)
      >>> geom.srid
      4326
      >>> round(geom.x), round(geom.y)  # transform is a bit lossy
      (1.0, 2.0)

    You can use an OGRGeometry with a projection::

      >>> ogr_with_srid = OGRGeometry('POINT (1 2)', srs=4326)
      >>> ogr_with_srid.srid
      4326
      >>> geom = geos_with_projection(ogr_with_srid)
      >>> geom.x, geom.y
      (1.0, 2.0)
      >>> geom.srid
      4326

    """
    geom = geom.clone()
    if geom.srs is None:
        if isinstance(projection, int):
            geom.srid = projection
        else:
            geom.srs = projection
    geom = geom.transform(projection, True)
    if hasattr(geom, 'geos'):
        geom = geom.geos
    return geom

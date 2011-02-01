#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of everyblock
#
#   everyblock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   everyblock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with everyblock.  If not, see <http://www.gnu.org/licenses/>.
#

from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry

class SfStreetManager(models.GeoManager):
    def get_intersection(self, street_a, street_b):
        """
        Returns the geometry of the intersection of the two streets, or None if it
        can't be determined.
        """
        from django.db import connection
        cursor = connection.cursor()
        table = self.model._meta.db_table
        cursor.execute("""
            SELECT ST_Intersection(a.location, b.location)
            FROM %s a, %s b
            WHERE a.name = %%s
                AND b.name = %%s
                AND ST_Intersects(a.location, b.location)
        """ % (table, table), (street_a, street_b))
        row = cursor.fetchone()
        if row:
            return GEOSGeometry(row[0])
        return None

    def get_intersection_by_cnn(self, cnn):
        """
        Returns the WKB of an intersection by CNN, or None if it doesn't exist.
        """
        try:
            return self.get(cnn=cnn).location
        except self.model.DoesNotExist:
            return None

class SfStreet(models.Model):
    name = models.CharField(max_length=36, db_index=True)
    cnn = models.CharField(max_length=8, db_index=True) # Centerline Network Number
    layer = models.CharField(max_length=16)
    location = models.LineStringField()
    objects = SfStreetManager()

    def __unicode__(self):
        return self.cnn

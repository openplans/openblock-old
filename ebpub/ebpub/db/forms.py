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

from ebpub.db import models
from django import forms
from django.contrib.gis.geos import MultiPolygon


def clean_location_avoid_geometrycollections(self):
    # Workaround for bug #95: if we get a GeometryCollection,
    # save it instead as a MultiPolygon, because PostGIS doesn't support
    # using Collections for anything useful like
    # ST_Intersects(some_other_geometry), so we effectively can't
    # use them at all. Yuck.
    locations = self.cleaned_data['location']
    if not isinstance(locations, list):
        locations = [locations]
    for i, loc in enumerate(locations):
        if loc.geom_type == 'GeometryCollection':
            polygons = []
            while loc.num_geom:
                next = loc.pop()
                if next.geom_type == 'Polygon':
                    polygons.append(next)
                elif next.geom_type == 'Point':
                    polygons.append((next.x, next.y), (next.x, next.y))
                else:
                    raise NotImplementedError("can't handle %r" % next.geom_type)
            loc = MultiPolygon(polygons)
        locations[i] = loc
    return locations

class LocationForm(forms.ModelForm):
    class Meta:
        model = models.Location

    clean_location = clean_location_avoid_geometrycollections


class NewsItemForm(forms.ModelForm):
    class Meta:
        model = models.NewsItem

    clean_location = clean_location_avoid_geometrycollections

    url = forms.URLField(widget=forms.TextInput(attrs={'size': 80}))

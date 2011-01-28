from ebpub.db import models
from django.forms import ModelForm
from django.contrib.gis.geos import MultiPolygon


def clean_location_avoid_geometrycolletions(self):
    # Workaround for bug #95: if we get a GeometryCollection,
    # save it instead as a MultiPolygon, because PostGIS doesn't support
    # using Collections for anything useful like
    # ST_Intersects(some_other_geometry), so we effectively can't
    # use them at all. Yuck.
    loc = self.cleaned_data['location']
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
    return loc

class LocationForm(ModelForm):
    class Meta:
        model = models.Location

    clean_location = clean_location_avoid_geometrycolletions


class NewsItemForm(ModelForm):
    class Meta:
        model = models.NewsItem

    clean_location = clean_location_avoid_geometrycolletions

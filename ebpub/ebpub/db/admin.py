from django.contrib.gis import admin
from ebpub.db.models import Location
from ebpub.db.models import LocationType
from ebpub.db.models import NewsItem
from ebpub.db.models import Schema
from ebpub.db.models import SchemaField
from ebpub.db.models import SchemaInfo


class NewsItemAdmin(admin.GeoModelAdmin):
    # Just need to inherit from GeoModelAdmin to get map-editable location.
    pass

class LocationAdmin(admin.GeoModelAdmin):
    # Just need to inherit from GeoModelAdmin to get map-editable location.
    pass

admin.site.register(Schema)
admin.site.register(SchemaField)
admin.site.register(SchemaInfo)
admin.site.register(NewsItem, NewsItemAdmin)
admin.site.register(LocationType)
admin.site.register(Location, LocationAdmin)


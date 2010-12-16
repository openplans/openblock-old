from django.contrib import admin
from ebpub.streets.models import Block, Street, BlockIntersection, \
    Intersection, Suburb, Place, StreetMisspelling

from ebpub.db.admin import OSMModelAdmin

class PlaceAdmin(OSMModelAdmin):
    pass

admin.site.register(Block)
admin.site.register(Street)
admin.site.register(BlockIntersection)
admin.site.register(Intersection)
admin.site.register(Suburb)
admin.site.register(Place, PlaceAdmin)
admin.site.register(StreetMisspelling)

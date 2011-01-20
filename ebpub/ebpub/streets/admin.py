from django.contrib import admin
from ebpub.streets.models import Block, Street, BlockIntersection, \
    Intersection, Suburb, StreetMisspelling

from ebpub.db.admin import OSMModelAdmin

admin.site.register(Block)
admin.site.register(Street)
admin.site.register(BlockIntersection)
admin.site.register(Intersection)
admin.site.register(Suburb)
admin.site.register(StreetMisspelling)

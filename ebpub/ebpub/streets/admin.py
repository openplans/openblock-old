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

from django.contrib import admin
from ebpub.streets.models import Block, Street, BlockIntersection, \
    Intersection, Suburb, Place, StreetMisspelling

from ebpub.geoadmin import OSMModelAdmin

class PlaceAdmin(OSMModelAdmin):
    list_display = ('pretty_name', 'address',)
    search_fields = ('pretty_name',)

class BlockAdmin(OSMModelAdmin):
    list_display = ('pretty_name', 'street', 'suffix', 'left_zip', 'right_zip', 'left_city', 'right_city')
    list_filter = ('suffix', 'left_city', 'right_city', 'left_zip', 'right_zip')
    search_fields = ('pretty_name',)

class StreetAdmin(OSMModelAdmin):
    list_display = ('pretty_name', 'suffix', 'city', 'state',)
    list_filter = ('suffix', 'city', 'state',)
    search_fields = ('pretty_name',)

class BlockIntersectionAdmin(OSMModelAdmin):
    list_display = ('block', 'intersecting_block', 'intersection',)
    raw_id_fields = ('block', 'intersecting_block', 'intersection',)
    search_fields = ('block__pretty_name',)

class IntersectionAdmin(OSMModelAdmin):
    list_display = ('pretty_name', 'zip', 'city', 'state')
    list_filter = ('zip', 'city', 'state')
    search_fields = ('pretty_name',)

class SuburbAdmin(OSMModelAdmin):
    pass

class StreetMisspellingAdmin(OSMModelAdmin):
    list_display = ('incorrect', 'correct',)
    search_fields = ('incorrect', 'correct',)


admin.site.register(Block, BlockAdmin)
admin.site.register(Street, StreetAdmin)
admin.site.register(BlockIntersection, BlockIntersectionAdmin)
admin.site.register(Intersection, IntersectionAdmin)
admin.site.register(Suburb, SuburbAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(StreetMisspelling, StreetMisspellingAdmin)

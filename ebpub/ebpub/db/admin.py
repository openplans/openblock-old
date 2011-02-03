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

from django.contrib.gis import admin
from ebpub.db.forms import LocationForm
from ebpub.db.forms import NewsItemForm
from ebpub.db.models import Attribute, Location, LocationType, NewsItem
from ebpub.db.models import Schema, SchemaField

from ebpub.geoadmin import OSMModelAdmin

class AttributeInline(admin.StackedInline):
    # TODO: this badly needs a custom Form that takes into account the
    # Schema and shows you only relevant fields, with labels.
    model = Attribute

class NewsItemAdmin(OSMModelAdmin):
    inlines = [
        AttributeInline,
        ]

    list_display = ('title', 'schema', 'item_date', 'pub_date', 'location_name')
    list_filter = ('schema',)
    form = NewsItemForm

class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_browsable', 'is_significant')
    list_filter = ('is_browsable', 'is_significant')

class LocationAdmin(OSMModelAdmin):
    form = LocationForm

    # This is populated by a trigger in ebpub/db/sql/location.sql.
    readonly_fields = ('area',)

class SchemaFieldAdmin(admin.ModelAdmin):
    list_filter = ('schema', 'is_lookup', 'is_filter', 'is_charted', 'is_searchable')


admin.site.register(Schema)
admin.site.register(SchemaField, SchemaFieldAdmin)
#admin.site.register(Attribute, AttributeAdmin)
admin.site.register(NewsItem, NewsItemAdmin)
admin.site.register(LocationType, LocationTypeAdmin)
admin.site.register(Location, LocationAdmin)


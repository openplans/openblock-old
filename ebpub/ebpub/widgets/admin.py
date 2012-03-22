#   Copyright 2011 OpenPlans and contributors
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
from ebpub.widgets.models import Template, Widget, PinnedItem

from ebpub.geoadmin import OSMModelAdmin


class WidgetAdmin(OSMModelAdmin):
    save_as = True
    prepopulated_fields = {'slug': ('name',)}

class TemplateAdmin(OSMModelAdmin):
    save_as = True

class PinnedItemAdmin(OSMModelAdmin):

    list_display = ('widget', 'news_item', 'item_number')

admin.site.register(Widget, WidgetAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(PinnedItem, PinnedItemAdmin)

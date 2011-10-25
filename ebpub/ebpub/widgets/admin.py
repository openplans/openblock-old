from django.contrib.gis import admin
from ebpub.widgets.models import Template, Widget, PinnedItem

from ebpub.geoadmin import OSMModelAdmin


class WidgetAdmin(OSMModelAdmin):
    save_as = True
    
class TemplateAdmin(OSMModelAdmin):
    save_as = True

class PinnedItemAdmin(OSMModelAdmin):

    list_display = ('widget', 'news_item', 'item_number')

admin.site.register(Widget, WidgetAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(PinnedItem, PinnedItemAdmin)
from django.contrib.gis import admin
from ebpub.widgets.models import Template, Widget

from ebpub.geoadmin import OSMModelAdmin


class WidgetAdmin(OSMModelAdmin):
    save_as = True
    
class TemplateAdmin(OSMModelAdmin):
    save_as = True

admin.site.register(Widget, WidgetAdmin)
admin.site.register(Template, TemplateAdmin)

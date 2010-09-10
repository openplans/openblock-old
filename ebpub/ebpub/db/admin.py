from django.contrib import admin
from ebpub.db.models import *

admin.site.register(Schema)
admin.site.register(SchemaField)
admin.site.register(SchemaInfo)
admin.site.register(NewsItem)
admin.site.register(LocationType)
admin.site.register(Location)

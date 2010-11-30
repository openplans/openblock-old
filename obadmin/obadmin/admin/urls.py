from django.conf.urls.defaults import *

urlpatterns = patterns('obadmin.admin.views',
    url(r'^old/$', 'index'),
    url(r'^old/schemas/$', 'schema_list'),
#    url(r'^old/schemas/(\d{1,6})/$', 'edit_schema'),
    url(r'^old/schemas/(\d{1,6})/lookups/(\d{1,6})/$', 'edit_schema_lookups'),
    url(r'^old/schemafields/$', 'schemafield_list'),
    url(r'^old/sources/$', 'blob_seed_list'),
    url(r'^old/sources/add/$', 'add_blob_seed'),
    url(r'^old/scraper-history/$', 'scraper_history_list'),
    url(r'^old/scraper-history/([-\w]{4,32})/$', 'scraper_history_schema'),
    url(r'^old/set-staff-cookie/$', 'set_staff_cookie'),
    url(r'^old/newsitems/(\d{1,6})/$', 'newsitem_details'),
    url(r'^old/geocoder-success-rates/$', 'geocoder_success_rates'),
)

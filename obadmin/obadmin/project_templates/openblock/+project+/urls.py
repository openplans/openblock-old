from django.conf.urls.defaults import *
from obadmin import admin

admin.autodiscover()

urlpatterns = patterns(

    '',

    (r'^admin/', include(admin.site.urls)),

    # ebpub provides all the UI for an openblock site.
    (r'^', include('ebpub.urls')),
)

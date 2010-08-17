from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(

    '',

    # EB admin site. Also need 2 additonal apps in settings.INSTALLED_APPS:
    # 'everyblock.admin' and 'everyblock.staticmedia'.
    (r'^ebadmin/', include('everyblock.admin.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the generic admin
    # (NOT COMPATIBLE WITH EVERYBLOCK/OPENBLOCK):
    #(r'^admin/', include(admin.site.urls)),

    (r'^api/newsitems.geojson/$', 'obdemo.views.newsitems_geojson'),

    # ebpub provides all the UI for an openblock site.
    (r'^', include('ebpub.urls')),

)

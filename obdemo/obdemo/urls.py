from django.conf import settings
from django.conf.urls.defaults import *
from obadmin import admin

admin.autodiscover()

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^(?P<path>(?:%s).*)$' % settings.DJANGO_STATIC_NAME_PREFIX.strip('/'),
         'django.views.static.serve', {'document_root': settings.EB_MEDIA_ROOT}),
    )
else:
    urlpatterns = patterns('')

urlpatterns += patterns(

    '',

    # EB admin site. Also need 2 additonal apps in settings.INSTALLED_APPS:
    # 'everyblock.admin' and 'everyblock.staticmedia'.
    #(r'^ebadmin/', include('everyblock.admin.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),

    (r'^disclaimer', 'django.views.generic.simple.direct_to_template',
     {'template': 'disclaimer.html'}),

    (r'^geotagger/$', 'obdemo.views.geotagger_ui'),

    # geotagger api
    (r'^', include('ebdata.geotagger.urls')),

    # ebpub provides nearly all the UI for an openblock site.
    (r'^', include('ebpub.urls')),


)

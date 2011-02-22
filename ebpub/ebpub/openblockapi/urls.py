from django.conf.urls.defaults import *
from ebpub.openblockapi import views

urlpatterns = patterns('',
    url(r'^$', views.check_api_available, name="check_api_available"),
)
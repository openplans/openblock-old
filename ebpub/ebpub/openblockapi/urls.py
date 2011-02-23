from django.conf.urls.defaults import *
from ebpub.openblockapi import views

urlpatterns = patterns(
    '',
    url(r'^$', views.check_api_available, name="check_api_available"),
    url(r'^items/types.json$', views.list_types_json, name="list_types_json"),
)

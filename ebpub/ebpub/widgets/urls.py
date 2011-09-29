from django.conf.urls.defaults import *
from ebpub.widgets import views

urlpatterns = patterns(
    '',
    url(r'api_raw_items/(?P<slug>[-_a-z0-9]{1,32})\/?$', views.ajax_widget_raw_items, name="ajax_widget_raw_items"),
    url(r'api_pins/(?P<slug>[-_a-z0-9]{1,32})\/?$', views.ajax_widget_pins, name="ajax_widget_pins"),
    url(r'(?P<slug>[-_a-z0-9]{1,32})\.js\/?$', views.widget_javascript, name="widget_javascript"),
    url(r'(?P<slug>[-_a-z0-9]{1,32})\/?$', views.widget_content, name="widget_content"),
)

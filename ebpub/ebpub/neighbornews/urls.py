from django.conf.urls.defaults import patterns, url
from ebpub.neighbornews import views

urlpatterns = patterns(
    '',
    url(r'^message/new/$', views.new_message, name="new_message"),
    url(r'^event/new/$', views.new_event, name="new_event"),
)

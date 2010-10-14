from django.conf.urls.defaults import *
from ebdata.geotagger import views

urlpatterns = patterns('',
    (r'^api/geocode/$', views.geocode),
    (r'^api/geotag/$', views.geotag),
)
from django.conf.urls.defaults import patterns, url, handler404, handler500
from ebpub.richmaps import views

urlpatterns = patterns(
    '',
    url(r'^$', views.bigmap, name="bigmap"),
    url(r'^popup/newsitem/(?P<item_id>.*)/?', views.item_popup, name="item_popup"),
    url(r'^popup/place/(?P<place_id>.*)/?', views.place_popup, name="place_popup"),
    url(r'^items.json/?', views.map_items_json, name="map_items_json"),
)

import datetime
from django.conf import settings
from django.contrib.gis import geos
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from ebpub.accounts.utils import login_required
from ebpub.db.models import Schema, NewsItem
from ebpub.utils.view_utils import eb_render
from ebpub.neighbornews.forms import NeighborMessageForm, NeighborEventForm
from ebpub.neighbornews.utils import if_disabled404, NEIGHBOR_MESSAGE_SLUG, NEIGHBOR_EVENT_SLUG

@if_disabled404(NEIGHBOR_MESSAGE_SLUG)
@login_required
def new_message(request):
    schema = Schema.objects.get(slug=NEIGHBOR_MESSAGE_SLUG)
    FormType = NeighborMessageForm
    return _new_usertype(request, schema, FormType, _create_message)
    
@if_disabled404(NEIGHBOR_EVENT_SLUG)
@login_required
def new_event(request):
    schema = Schema.objects.get(slug=NEIGHBOR_EVENT_SLUG)
    FormType = NeighborEventForm
    return _new_usertype(request, schema, FormType, _create_event)

def _new_usertype(request, schema, FormType, create_item):
    if request.method == 'POST': 
        form = FormType(request.POST)
        if form.is_valid():
            item = create_item(request, schema, form)
            detail_url = reverse('ebpub-newsitem-detail', args=(schema.slug, '%d' % item.id))
            return HttpResponseRedirect(detail_url)
    else:
        form = FormType()
        
    mapconfig = {
        'locations': [],
        'layers': [],
        'baselayer_type': settings.MAP_BASELAYER_TYPE,

    }
    ctx = {
        'form': form,
        'map_configuration': mapconfig,
        'default_lon': settings.DEFAULT_MAP_CENTER_LON,
        'default_lat': settings.DEFAULT_MAP_CENTER_LAT,
        'default_zoom': settings.DEFAULT_MAP_ZOOM,
        'schema': schema
    }
    return eb_render(request, "neighbornews/new_message.html", ctx)

def _create_event(request, schema, form):
    item = _create_item(request, schema, form)
    item.attributes['start_time'] = form.cleaned_data['start_time']
    item.attributes['end_time'] = form.cleaned_data['end_time']
    item.save()
    return item

def _create_message(request, schema, form):
    return _create_item(request, schema, form)

def _create_item(request, schema, form):
    item = NewsItem(schema=schema)

    # common attributes
    for attr in ('title', 'description', 'location_name', 'url'): 
        setattr(item, attr, form.cleaned_data[attr])
    
    # location 
    lon = form.cleaned_data['longitude']
    lat = form.cleaned_data['latitude']
    item.location = geos.Point(lon, lat)


    # maybe specified ...
    if 'item_date' in form.cleaned_data: 
        item.item_date = form.cleaned_data['item_date']
    else:
        item.item_date = datetime.datetime.now().date()
    item.pub_date = datetime.datetime.now()
    item.save()
    
    return item



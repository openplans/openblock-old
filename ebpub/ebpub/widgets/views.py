from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, Template
from django.template.context import RequestContext
from django.utils import simplejson as json
from ebpub.accounts.utils import login_required
from ebpub.db.models import NewsItem
from ebpub.utils.logutils import log_exception
from ebpub.widgets.models import Widget, PinnedItem
import datetime
from operator import attrgetter

def widget_javascript(request, slug):
    """
    View that returns javascript suitable for linking to from an embedded script tag.
    The javsacript renders the widget using its template, once, on page load.
    """
    try:
        widget = Widget.objects.get(slug=slug)
    except Widget.DoesNotExist:
        return HttpResponse(status=404)

    payload = json.dumps(render_widget(widget))
    return render_to_response('widgets/widget.js', {'payload': payload, 'target': widget.target_id},
                              mimetype="text/javascript")

def widget_content(request, slug):
    """
    View that renders the widget using its template.
    """
    try:
        widget = Widget.objects.get(slug=slug)
    except Widget.DoesNotExist:
        return HttpResponse(status=404)
    return HttpResponse(render_widget(widget), status=200,
                        mimetype=widget.template.content_type)

def render_widget(widget, items=None):
    """Returns an HTML string of the widget rendered using its template.
    """
    if items is None:
        items = widget.fetch_items()
    info = {
        'items': [template_context_for_item(x, widget) for x in items],
        'widget': widget
    }
    # TODO: cache template compilation
    t = Template(widget.template.code)
    return t.render(Context(info))

def template_context_for_item(newsitem, widget):
    # try to make something ... reasonable for use in
    # templates.
    ctx = {
        'attributes': [],
        'attributes_by_name': {},
    }
    for att in newsitem.attributes_for_template():

        attr = {
            'name': att.sf.name,
            'title': att.sf.smart_pretty_name(),
            'display': att.sf.display
        }

        vals = [x['value'] for x in att.value_list()]
        if len(vals) == 1:
            attr['value'] = vals[0]
            attr['is_list'] = False
        else:
            attr['value'] = vals
            attr['is_list'] = True
        ctx['attributes'].append(attr)
        ctx['attributes_by_name'][att.sf.name] = attr

    # newsitem fields
    ctx['id'] = newsitem.id
    ctx['schema'] = newsitem.schema
    ctx['title'] = newsitem.title
    ctx['description'] = newsitem.description
    ctx['pub_date'] = newsitem.pub_date
    ctx['item_date'] = newsitem.item_date
    ctx['location'] = {}
    if newsitem.location:
        ctx['location']['lon'] = newsitem.location.x
        ctx['location']['lat'] = newsitem.location.y
    ctx['location']['name'] = newsitem.location_name

    ctx['external_url'] =  newsitem.url
    if newsitem.schema.has_newsitem_detail:
        ctx['internal_url'] = 'http://' + settings.EB_DOMAIN + newsitem.item_url()

    # overlapping Locations, by type.
    # This is a callable so you only pay for it if you access it.
    def intersecting_locations_for_item():
        from ebpub.db.models import Location
        locations = Location.objects.filter(location__intersects=newsitem.location)
        # TODO: we join on LocationType a bunch here. Can we cache those or do something faster?
        locations = locations.select_related()
        by_type = {}
        for loc in locations:
            # Assume there is at most one intersecting location of each type.
            # That will probably be wrong somewhere someday...
            # eg. neighborhoods with fuzzy borders.
            by_type[loc.location_type.slug] = loc
        return by_type

    ctx['intersecting'] = intersecting_locations_for_item

    if widget.item_link_template and widget.item_link_template.strip():
        try:
            ctx['internal_url'] = _eval_item_link_template(widget.item_link_template,
                                                           {'item': ctx, 'widget': widget})
        except:
            log_exception()
            # TODO: some sort of error handling
            return '#error'

    return ctx

def _eval_item_link_template(template, context):
    t = Template(template)
    return t.render(Context(context)).strip()

##########################################################################
#
# special widget administration API views
#
##########################################################################

@login_required
def widget_admin_list(request):
    """
    List of widgets for custom separate admin UI
    """
    if not request.user.is_superuser == True:
        return HttpResponse("You must be an administrator to access this function.",
                            status=401)
    ctx = RequestContext(request, {'widgets': Widget.objects.all()})
    return render_to_response('widgets/stickylist.html', ctx)


@login_required
def widget_admin(request, slug):
    """
    Custom view for administering pinned items
    """
    if not request.user.is_superuser == True:
        return HttpResponse("You must be an administrator to access this function.", status=401)

    widget = get_object_or_404(Widget.objects, slug=slug)

    ctx = RequestContext(request, {'widget': widget})
    return render_to_response('widgets/sticky.html', ctx)



@login_required
def ajax_widget_raw_items(request, slug):
    """
    gets a list of 'raw' items in a widget (does not include
    pinned items)

    start and count parameters may be added as query parameters
    to retrieve more items.  by default the call returns items
    in the range [0,widget.max_items)

    Example of the structure returned:

    {
        "items": [
            {
                "id': 1234,
                "title": "Some Item",
            },
            ...
        ],
        "start": 0
    }

    """
    if not request.user.is_superuser == True:
        return HttpResponse("You must be an administrator to access this function.", status=401)

    widget = get_object_or_404(Widget.objects, slug=slug)

    try:
        start = int(request.GET.get('start', 0))
        count = int(request.GET.get('count', widget.max_items))
    except:
        return HttpResponse(status=400)

    items = widget.raw_item_query(start, count).all()
    item_infos = []
    for item in items:
        item_info = {
            'id': item.id,
            'title': item.title,
        }
        item_infos.append(item_info)

    info = {'items': item_infos, 'start': start}
    return HttpResponse(json.dumps(info), mimetype="application/json")


@login_required
def ajax_widget_pins(request, slug):
    """
    view that exposes and allows setting of 'pinned' items
    in a widget.

    Example of the structure returned/accepted:

    {
        "items": [
            {
                "id': 1234,
                "index": 0,
                "title": "Some Item",
                "expiration_date": "12/30/2040",
                "expiration_time": "09:45 PM" // 12 hour
            },
            {
                "id': 1235,
                "index": 7,
                "title": "Some Other Item",
                // no expiration
            },
            ...
        ]
    }

    """

    if not request.user.is_superuser == True:
        return HttpResponse("You must be an administrator to access this function.", status=401)

    widget = get_object_or_404(Widget.objects, slug=slug)

    if request.method == 'GET':
        return _get_ajax_widget_pins(request, widget)
    elif request.method == 'POST': 
        return _set_ajax_widget_pins(request, widget)
    else:
        return HttpResponseNotAllowed(["GET", "PUT"])

def _get_ajax_widget_pins(request, widget):
    """
    retrieves a json structure that describes the
    items currently "pinned" in a widget as described
    in ajax_widget_pins.
    """

    pins = list(PinnedItem.objects.filter(widget=widget).all())
    pins.sort(key=attrgetter('item_number'))

    item_infos = []
    for pin in pins:
        item_info = {
            'id': pin.news_item.id,
            'title': pin.news_item.title,
            'index': pin.item_number
        }
        if pin.expiration_date is not None:
            item_info['expiration_date'] = pin.expiration_date.date().strftime('%m/%d/%Y')
            item_info['expiration_time'] = pin.expiration_date.time().strftime('%I:%M%p')

        item_infos.append(item_info)

    info = {'items': item_infos}
    return HttpResponse(json.dumps(info), mimetype="application/json")

def _set_ajax_widget_pins(request, widget):
    """
    Sets pinned items in a widget based a json structure
    as described in ajax_widget_pins.

    Any existing pins are removed and replaced by the pins described in
    the given structure.
    """

    try:
        pin_info = json.loads(request.raw_post_data)
    except:
        return HttpResponse("Unable to parse json body", status=400)

    new_pins = []
    for pi in pin_info['items']:
        ni = NewsItem.objects.get(id=pi['id'])
        new_pin = PinnedItem(news_item=ni, widget=widget, item_number=pi['index'])
        expiration = None
        if 'expiration_date' in pi:
            try:
                expiration = datetime.datetime.strptime(pi['expiration_date'], '%m/%d/%Y')
            except:
                return HttpResponse("unable to parse expiration date %s" % pi['expiration_date'], status=400)
        if 'expiration_time' in pi: 
            if expiration is None: 
                return HttpResponse("cannot specify expiration time without expiration date", status=400)
            try:
                etime = datetime.datetime.strptime(pi['expiration_time'], '%I:%M%p')
                expiration = expiration.replace(hours=etime.hours, minutes=etime.minutes)
            except:
                return HttpResponse("unable to parse expiration time %s" % pi['expiration_time'], status=400)
        if expiration is not None: 
            new_pin.expiration_date = expiration
        new_pins.append(new_pin)

    # destroy current pins
    PinnedItem.objects.filter(widget=widget).delete()
    for pin in new_pins: 
        pin.save()
        
    if len(new_pins) > 0: 
        return HttpResponse(status=201)
    else: 
        return HttpResponse(status=200)

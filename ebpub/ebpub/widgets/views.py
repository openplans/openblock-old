#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, Template
from django.template.context import RequestContext
from django.utils import simplejson as json
from ebpub.accounts.utils import login_required
from ebpub.db.models import NewsItem
from ebpub.widgets.models import Widget, PinnedItem
from operator import attrgetter
import datetime
import logging

logger = logging.getLogger('ebpub.widgets.views')

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
    code = widget.template.code
    if not ' load eb ' in code:
        # Convenience so template authors don't have to remember this detail.
        code = '{% load eb %}\n' + code
    t = Template(code)
    return t.render(Context(info))

def template_context_for_item(newsitem, widget=None):
    # try to make something ... reasonable for use in
    # templates.
    ctx = {
        'attributes': [],
        'attributes_by_name': {},
        '_item': newsitem,  # cached in case downstream code really needs it.
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
        # TODO: Is centroid really what we want for non-Point geometries?
        ctx['location']['lon'] = newsitem.location.centroid.x
        ctx['location']['lat'] = newsitem.location.centroid.y
        ctx['location']['geom'] = newsitem.location

    ctx['location']['name'] = newsitem.location_name

    ctx['external_url'] =  newsitem.url
    if newsitem.schema.has_newsitem_detail:
        ctx['internal_url'] = 'http://' + settings.EB_DOMAIN + newsitem.item_url()

    if widget is not None:
        if widget.item_link_template and widget.item_link_template.strip():
            try:
                ctx['internal_url'] = _eval_item_link_template(widget.item_link_template,
                                                               {'item': ctx, 'widget': widget})
            except:
                logger.exception('failed to create link for widget')
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

    ctx = RequestContext(request, {'widget': widget,
                                   'max_items_range': range(widget.max_items),
                                   })
    return render_to_response('widgets/sticky.html', ctx)



@login_required
def ajax_widget_raw_items(request, slug):
    """
    gets a list of 'raw' items in a widget (does not include
    pinned items), as a JSON object.

    start and count parameters may be added as query parameters
    to retrieve more items.  by default the call returns items
    in the range [0,widget.max_items)

    Example of the structure returned:

    .. code-block:: javascript

     {
        "items": [
            {
                "id': 1234,
                "title": "Some Item",
            }
            // ...
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
    except ValueError:
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
    '''
    view that exposes and allows setting of "pinned" items
    in a widget.

    Example of the structure returned/accepted:

    .. code-block:: javascript

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
            // ...
         ]
      }
    '''

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
    # Retrieves a json structure that describes the
    # items currently "pinned" in a widget as described
    # in ajax_widget_pins.
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
    # Sets pinned items in a widget based a json structure
    # as described in ajax_widget_pins.
    #
    # Any existing pins are removed and replaced by the pins described in
    # the given structure.
    try:
        pin_info = json.loads(request.raw_post_data)
    except ValueError:
        logger.exception('bad json')
        return HttpResponse("Unable to parse json body", status=400)

    new_pins = []
    for pi in pin_info['items']:
        ni = NewsItem.objects.get(id=pi['id'])
        new_pin = PinnedItem(news_item=ni, widget=widget, item_number=pi['index'])
        expiration = None
        if pi.get('expiration_date'):
            try:
                expiration = datetime.datetime.strptime(pi['expiration_date'], '%m/%d/%Y')
            except ValueError:
                return HttpResponse("unable to parse expiration date %s" % pi['expiration_date'], status=400)
        if pi.get('expiration_time', '').strip():
            if expiration is None:
                return HttpResponse("cannot specify expiration time without expiration date", status=400)
            # Be slightly broad about time formats accepted.
            etime = pi['expiration_time'].replace(' ', '').lower()
            try:
                if etime.endswith('am') or etime.endswith('pm'):
                    etime = datetime.datetime.strptime(etime, '%I:%M%p')
                else:
                    # Assume it's 24-hour.
                    etime = datetime.datetime.strptime(etime, '%H:%M')
            except ValueError:
                return HttpResponse("unable to parse expiration time %s" % pi['expiration_time'], status=400)
            expiration = expiration.replace(hour=etime.hour, minute=etime.minute)

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

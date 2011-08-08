from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, Template
from django.utils import simplejson as json
from ebpub.widgets.models import Widget
import urlparse

def widget_javascript(request, slug):
    try:
        widget = Widget.objects.get(slug=slug)
    except Widget.DoesNotExist:
        return HttpResponse(status=404)

    payload = json.dumps(render_widget(widget))
    return render_to_response('widgets/widget.js', {'payload': payload, 'target': widget.target_id},
                              mimetype="text/javascript")
    
def widget_content(request, slug):
    try:
        widget = Widget.objects.get(slug=slug)
    except Widget.DoesNotExist:
        return HttpResponse(status=404)
        
    return HttpResponse(render_widget(widget), status=200,
                        mimetype=widget.template.content_type)

def render_widget(widget, items=None):
    if items is None:
        items = widget.fetch_items()
    info = {
        'items': [_template_ctx(x, widget) for x in items], 
        'widget': widget
    }
    # TODO: cache template compilation
    t = Template(widget.template.code)
    return t.render(Context(info))

def template_context_for_item(newsitem):
    # try to make something ... reasonable for use in 
    # templates. 
    ctx = {
        'attributes': [],
        'attributes_by_name': {},
    }
    for att in newsitem.attributes_for_template():
        if not att.sf.display:
            continue

        attr = {
            'name': att.sf.name,
            'title': att.sf.smart_pretty_name(),
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

    return ctx

def _template_ctx(newsitem, widget):
    ctx = template_context_for_item(newsitem)

    # now to extra widgety-stuff
    if widget.item_link_template and widget.item_link_template.strip():
        try:
            ctx['internal_url'] = _eval_item_link_template(widget.item_link_template, ctx)
        except: 
            return '#error'
    
    return ctx

def _eval_item_link_template(template, context): 
    t = Template(template)
    return t.render(Context(context)).strip()
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

    payload = json.dumps(_render_widget(widget))
    return render_to_response('widgets/widget.js', {'payload': payload, 'target': widget.target_id},
                              mimetype="text/javascript")
    
def widget_content(request, slug):
    try:
        widget = Widget.objects.get(slug=slug)
    except Widget.DoesNotExist:
        return HttpResponse(status=404)
        
    return HttpResponse(_render_widget(widget), status=200,
                        mimetype=widget.template.content_type)

def _render_widget(widget):
    info = {
        'items': [_template_ctx(x, widget) for x in widget.fetch_items()],
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
    ctx['schema'] = newsitem.schema
    ctx['title'] = newsitem.title
    ctx['description'] = newsitem.description
    ctx['pub_date'] = newsitem.pub_date
    ctx['item_date'] = newsitem.item_date
    ctx['location'] = {}
    if newsitem.location: 
        ctx['location']['lat'] = newsitem.location.x,
        ctx['location']['lon'] = newsitem.location.y
    ctx['location']['name'] = newsitem.location_name

    ctx['external_url'] =  newsitem.url
    if newsitem.schema.has_newsitem_detail:
        ctx['internal_url'] = 'http://' + settings.EB_DOMAIN + newsitem.item_url()

    return ctx

def _template_ctx(newsitem, widget):
    ctx = template_context_for_item(newsitem)
    # now to extra widgety-stuff
    ctx['external_url'] = _mutate_link(newsitem.url, widget)
    if newsitem.schema.has_newsitem_detail:
        ctx['internal_url'] = _mutate_link('http://' + settings.EB_DOMAIN + newsitem.item_url(), widget)
    return ctx
    
def _mutate_link(url, widget): 
    if not widget.extra_link_parameters:
        return url 
    
    suffix = widget.extra_link_parameters
    pr = list(urlparse.urlsplit(url))
    
    # if there is a query string already, append with &
    if len(pr[3]):
        pr[3] = '%s&%s' % (pr[3], suffix)
    else: 
        pr[3] = suffix
        
    return urlparse.urlunsplit(pr)
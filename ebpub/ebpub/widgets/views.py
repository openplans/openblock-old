from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, Template
from django.utils import simplejson as json
from ebpub.widgets.models import Widget


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
        'items': [_template_ctx(x) for x in widget.fetch_items()],
        'widget': widget
    }
    # TODO: cache template compilation
    t = Template(widget.template.code)
    return t.render(Context(info))
    
def _template_ctx(newsitem):
    # try to make something ... reasonable for use in 
    # widget templates. 
    ctx = {
        'attributes': [],
        'attributes_by_name': {},
    }
    for att in newsitem.attributes_for_template():
        if not att.sf.display:
            continue

        attr = {
            'name': att.sf.name,
            'title': att.sf.smart_pretty_name,
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
    ctx['location'] = newsitem.location

    ctx['external_url'] = newsitem.url
    if newsitem.schema.has_newsitem_detail:
        ctx['internal_url'] = newsitem.item_url()

    return ctx
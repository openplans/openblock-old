from django.http import HttpResponse
from ebpub.db import models
from django.utils import simplejson

def check_api_available(request):
    """
    endpoint to indicate that this version of the API
    is available.
    """
    return HttpResponse(status=200)


def list_types_json(request):
    """
    List the known NewsItem types (Schemas).
    """
    schemas = []
    for schema in models.Schema.public_objects.all():
        fields = {}
        for sf in schema.schemafield_set.all():
            if sf.is_lookup:
                fieldtype = 'text'
            else:
                fieldtype = sf.datatype
                if fieldtype == 'varchar':
                    fieldtype = 'text'
            fields[sf.slug] = {
                'pretty_name': sf.smart_pretty_name(),
                'type': fieldtype,
                # TODO: what else?
                }
            # TODO: should we enumerate known values of Lookups?
        schemas.append({
                'id': schema.id,
                'indefinite_article': schema.indefinite_article,
                'last_updated': schema.last_updated.strftime('%Y-%m-%d'),
                'name': schema.name,
                'plural_name': schema.plural_name,
                'slug': schema.slug,
                'fields': fields,
                })
    output = simplejson.dumps(schemas, indent=1)
    return HttpResponse(output, mimetype="application/javascript")


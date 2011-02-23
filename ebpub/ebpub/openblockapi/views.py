from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.utils import simplejson
from ebpub.db import models

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
    schemas = {}
    for schema in models.Schema.public_objects.all():
        attributes = {}
        for sf in schema.schemafield_set.all():
            if sf.is_lookup:
                fieldtype = 'text'
            else:
                fieldtype = sf.datatype
                if fieldtype == 'varchar':
                    fieldtype = 'text'
            attributes[sf.slug] = {
                'pretty_name': sf.smart_pretty_name(),
                'type': fieldtype,
                # TODO: what else?
                }
            # TODO: should we enumerate known values of Lookups?
        schemas[schema.slug] = {
                'indefinite_article': schema.indefinite_article,
                'last_updated': schema.last_updated.strftime('%Y-%m-%d'),
                'name': schema.name,
                'plural_name': schema.plural_name,
                'slug': schema.slug,
                'attributes': attributes,
                }

    response = HttpResponse(mimetype="application/javascript")
    simplejson.dump(schemas, response, indent=1)
    return response

def locations_json(request):
    # TODO: this will obsolete ebpub.db.views.ajax_location_list
    locations = models.Location.objects.filter(is_public=True).order_by('display_order').select_related().defer('location')
    result = [{'slug': loc.slug, 'name': loc.name, 'city': loc.city,
               'type': loc.location_type.slug,
               'description': loc.description or '',
               'geojson_url': reverse('location_detail_json', kwargs={'slug': loc.slug})}
              for loc in locations]
    response = HttpResponse(mimetype='application/javascript')
    simplejson.dump(result, response, indent=1)
    return response

def location_detail_json(request, slug):
    # TODO: this will obsolete ebpub.db.views.ajax_location
    try:
        location = models.Location.objects.geojson().get(slug=slug)
    except (ValueError, models.Location.DoesNotExist):
        raise Http404()
    geojson = {'type': 'Feature',
               # The queryset already cooked up a geojson string,
               # but there's no convenient way to embed it in our output
               # except by doing string substitution, so we put a dummy here.
               'geometry': '--REPLACE--',
               'properties': {'type': location.location_type.slug,
                              'slug': location.slug,
                              'source': location.source,
                              'description': location.description,
                              'centroid': (location.centroid or location.location.centroid).wkt,
                              'area': location.area,
                              'population': location.population,
                              'city': location.city,
                              }
               }
    geojson = simplejson.dumps(geojson, indent=1)
    geojson = geojson.replace('"--REPLACE--"', location.geojson)
    response = HttpResponse(geojson, mimetype='application/javascript')
    return response

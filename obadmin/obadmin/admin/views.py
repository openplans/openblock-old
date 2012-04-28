#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#

# -*- coding: utf-8 -*-
from background_task.models import Task
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.helpers import Fieldset
from django.contrib.gis.gdal import DataSource
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_protect
from ebdata.blobs.create_seeds import create_rss_seed
from ebdata.blobs.models import Seed
from ebdata.scrapers.general.spreadsheet import retrieval
from ebpub.db.models import LocationType
from ebpub.db.models import Schema, SchemaField, NewsItem, Lookup, DataUpdate
from . import forms

import logging

logger = logging.getLogger('obadmin.admin.views')

# Returns the username for a given request, taking into account our proxy
# (which sets HTTP_X_REMOTE_USER).
request_username = lambda request: request.META.get('REMOTE_USER', '') or request.META.get('HTTP_X_REMOTE_USER', '')

user_is_staff = lambda username: settings.DEBUG


def index(request):
    return render_to_response('obadmin/index.html', {})


def schema_list(request):
    s_list = []
    for s in Schema.objects.order_by('name'):
        s_list.append({
            'schema': s,
            'lookups': s.schemafield_set.filter(is_lookup=True).order_by('pretty_name_plural'),
        })
    return render_to_response('obadmin/schema_list.html', {'schema_list': s_list})


def set_staff_cookie(request):
    r = HttpResponseRedirect('../')
    r.set_cookie(settings.STAFF_COOKIE_NAME, settings.STAFF_COOKIE_VALUE)
    return r


def edit_schema_lookups(request, schema_id, schema_field_id):
    s = get_object_or_404(Schema, id=schema_id)
    sf = get_object_or_404(SchemaField, id=schema_field_id, schema__id=s.id, is_lookup=True)
    lookups = Lookup.objects.filter(schema_field__id=sf.id).order_by('name')
    lookup_ids = [look.id for look in lookups]
    if request.method == 'POST':
        form = forms.SchemaLookupsForm(lookup_ids, request.POST)
        if form.is_valid():
            # Save any lookup values that changed.
            for look in lookups:
                name = request.POST.get('%s-name' % look.id)
                description = request.POST.get('%s-description' % look.id)
                if name is not None and description is not None and (name != look.name or description != look.description):
                    look.name = name
                    look.description = description
                    look.save()
            return HttpResponseRedirect('../../../')
    else:
        initial = {}
        for look in lookups:
            initial['%s-name' % look.id] = look.name
            initial['%s-description' % look.id] = look.description
        form = forms.SchemaLookupsForm(lookup_ids, initial=initial)
    context = RequestContext(request,
                             {'schema': s, 'schema_field': sf, 'form': list(form)})
    return render_to_response('obadmin/edit_schema_lookups.html',
                              context_instance=context)


def schemafield_list(request):
    sf_list = SchemaField.objects.select_related().order_by('db_schema.name', 'display_order')
    return render_to_response('obadmin/schemafield_list.html', {'schemafield_list': sf_list})


def geocoder_success_rates(request):
    from django.db import connection
    sql = """
        select s.plural_name, count(ni.location) as geocoded, count(*) as total
        from db_newsitem ni
        inner join db_schema s
        on s.id=ni.schema_id
        group by s.plural_name
        order by count(ni.location)::float / count(*)::float;
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    schema_list = [{'name': r[0], 'geocoded': r[1], 'total': r[2], 'ratio': float(r[1]) / float(r[2])} for r in results]
    return render_to_response('obadmin/geocoder_success_rates.html', {'schema_list': schema_list})


def blob_seed_list(request):
    s_list = Seed.objects.order_by('autodetect_locations', 'pretty_name').filter(is_rss_feed=True)
    return render_to_response('obadmin/blob_seed_list.html', {'seed_list': s_list})


def add_blob_seed(request):
    if request.method == 'POST':
        form = forms.BlobSeedForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            create_rss_seed(cd['rss_url'], cd['site_url'], cd['rss_full_entry'], cd['pretty_name'], cd['guess_article_text'], cd['strip_noise'])
            return HttpResponseRedirect('../')
    else:
        form = forms.BlobSeedForm()
    context = RequestContext(request, {'form': form})
    return render_to_response('obadmin/add_blob_seed.html', context_instance=context)


def scraper_history_list(request):
    schema_ids = [i['schema'] for i in DataUpdate.objects.select_related().order_by('schema__plural_name').distinct().values('schema')]
    s_dict = Schema.objects.in_bulk(schema_ids)
    s_list = [s_dict[i] for i in schema_ids]
    return render_to_response('obadmin/scraper_history_list.html', {'schema_list': s_list})


def scraper_history_schema(request, slug):
    s = get_object_or_404(Schema, slug=slug)
    du_list = DataUpdate.objects.filter(schema__id=s.id).order_by('schema__name', '-update_start')
    return render_to_response('obadmin/scraper_history_schema.html', {'schema': s, 'dataupdate_list': du_list})


def newsitem_details(request, news_item_id):
    """
    Shows all of the raw values in a NewsItem for debugging.
    """
    ni = get_object_or_404(NewsItem, pk=news_item_id)
    real_names = [
        'varchar01', 'varchar02', 'varchar03', 'varchar04', 'varchar05',
        'date01', 'date02', 'date03', 'date04', 'date05',
        'time01', 'time02',
        'datetime01', 'datetime02', 'datetime03', 'datetime04',
        'bool01', 'bool02', 'bool03', 'bool04', 'bool05',
        'int01', 'int02', 'int03', 'int04', 'int05', 'int06', 'int07',
        'text01'
    ]
    schema_fields = {}
    for sf in SchemaField.objects.filter(schema=ni.schema):
        schema_fields[sf.real_name] = sf
    attributes = []
    for real_name in real_names:
        schema_field = schema_fields.get(real_name, None)
        attributes.append({
            'real_name': real_name,
            'name': schema_field and schema_field.name or None,
            'raw_value': schema_field and ni.attributes[schema_field.name] or None,
            'schema_field': schema_field,
        })
    return render_to_response('obadmin/news_item_detail.html', {
        'news_item': ni, 'attributes': attributes
    })


def jobs_status(request, appname, modelname):
    """
    Returns HTML fragment about current background tasks, intended for
    use via AJAX.
    """
    pending = Task.objects.find_available()
    running = Task.objects.filter(locked_by__isnull=False)
    # if there are old jobs and nothing's running, tell user to run tasks
    old_time = datetime.now() - timedelta(seconds=(60 * 15))
    stalled_count = pending.filter(run_at__lt=old_time).count()
    if stalled_count > 0 and pending.filter(locked_at__isnull=False).count() == 0:
        return HttpResponse("Queued jobs aren't being run. Is 'django-admin.py process_tasks' running?")

    # list instead of dict because tasks run in sequence, confusing otherwise
    if appname == 'db':
        counts = [
            {'label': u'Download state shapefile',
             'task': u'obadmin.admin.tasks.download_state_shapefile' },
            {'label': u'Import ZIP code',
             'task': u'obadmin.admin.tasks.import_zip_from_shapefile'},
            {'label': 'Import Location',
             'task': u'obadmin.admin.tasks.import_location'},
            ]
    elif appname == 'streets':
        # Don't bother discriminating further based on modelname;
        # the models here are closely related anyway.
        counts = [
            {'label': u'Import blocks from shapefile',
             'task': u'obadmin.admin.tasks.import_blocks_from_shapefiles'},
            {'label': 'Populate streets',
             'task': u'obadmin.admin.tasks.populate_streets_task'},
            {'label': 'Populate block intersections',
             'task': u'obadmin.admin.tasks.populate_block_intersections'},
            {'label': 'Populate intersections',
             'task': u'obadmin.admin.tasks.populate_intersections'},
            ]
    else:
        raise ValueError("No known tasks for %s/%s" % (appname, modelname))

    display_counts = False
    for task in counts:
        task['pending_count'] = pending.filter(task_name=task['task']).count()
        task['running_count'] = running.filter(task_name=task['task']).count()

        if task['pending_count'] or task['running_count']:
            display_counts = True

    if display_counts:
        return render(request, 'obadmin/jobs_status.html', {
          'counts': counts,
        })
    else:
        return HttpResponse("No background tasks running.")


@csrf_protect
def import_zipcode_shapefiles(request):
    form = forms.ImportZipcodeShapefilesForm(request.POST or None)
    if form.save():
        return HttpResponseRedirect('../')
    fieldset = Fieldset(form, fields=('state', 'zip_codes',))
    return render(request, 'obadmin/location/import_zip_shapefiles.html', {
      'fieldset': fieldset,
      'form': form,
    })


@csrf_protect
def upload_shapefile(request):
    form = forms.UploadShapefileForm(request.POST or None, request.FILES or None)
    if form.save():
        return HttpResponseRedirect('../pick-shapefile-layer/?shapefile=%s' % form.shp_path)

    fieldset = Fieldset(form, fields=('zipped_shapefile',))
    return render(request, 'obadmin/location/upload_shapefile.html', {
      'fieldset': fieldset,
      'form': form,
    })


@csrf_protect
def pick_shapefile_layer(request):
    form = forms.PickShapefileLayerForm(request.POST or None)
    shapefile = request.GET.get('shapefile', False)
    if not shapefile:
        shapefile = request.POST.get('shapefile', False)
    if not shapefile:
        return HttpResponseRedirect('../upload-shapefile/')
    if form.save():
        return HttpResponseRedirect('../')
    if form.failure_msgs:
        for msg in form.failure_msgs:
            messages.error(request, msg)

    try:
        ds = DataSource(shapefile)
    except Exception as e:
        ds = None
        messages.error(request, "Error opening shapefile: %s" % e)
        logger.exception("Unhandled error opening shapefile:")

    fieldset = Fieldset(form, fields=('location_type',))
    return render(request, 'obadmin/location/pick_shapefile_layer.html', {
        'shapefile': shapefile,
        'layers': ds,
        'location_types': LocationType.objects.all(),
        'fieldset': fieldset,
    })


@csrf_protect
def import_blocks(request):
    form = forms.ImportBlocksForm(request.POST or None, request.FILES or None)
    if form.save():
        return HttpResponseRedirect('../')

    fieldsets = (
        Fieldset(form, fields=('edges', 'featnames', 'faces', 'place')),
        Fieldset(form, fields=('reset', 'city', 'fix_cities', 'regenerate_intersections')),
        )

    return render(request, 'obadmin/block/import_blocks.html', {
        'fieldsets': fieldsets,
        'form': form,
    })


def import_items_from_spreadsheets(items_file, schema, mapping_file=None,
                                   unique_fields=None):
    """
    Imports NewsItems from the given files; returns
    (number added, number changed, number skipped).
    """
    scraper = retrieval.SpreadsheetScraper(items_file,
                                           map_sheet_file=mapping_file,
                                           schema_slug=schema.slug,
                                           unique_fields=unique_fields,
                                           )
    scraper.update()
    return (scraper.num_added, scraper.num_changed, scraper.num_skipped)


@csrf_protect
def import_newsitems(request):
    from ebdata.scrapers.general.spreadsheet.retrieval import get_default_unique_field_names
    form = forms.ImportNewsForm(
        request.POST or None, request.FILES or None,
        initial={'unique_fields': get_default_unique_field_names()}
        )
    if form.save():
        # TODO: Capture logging output and put that in message too?
        msg = u'%d added. %d updated. %d skipped or unchanged.' % (form.added, form.updated, form.skipped)
        msg += u' See the server error log if you need more info.'
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect('./')

    fieldsets = (
        Fieldset(form, fields=('items_file', 'schema', 'mapping_file', 'unique_fields')),
        )

    return render(request, 'obadmin/import_news.html', {
        'form': form,
        'fieldsets': fieldsets,
    })


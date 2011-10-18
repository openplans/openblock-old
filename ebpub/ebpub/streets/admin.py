#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
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

import csv
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.gis import geos
from django.contrib.gis.measure import D
from django.core.exceptions import PermissionDenied
from django import forms, template
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from ebpub.utils.logutils import log_exception
from ebpub.streets.models import Block, Street, BlockIntersection, \
    Intersection, Suburb, Place, PlaceType, PlaceSynonym, StreetMisspelling
from ebpub.geocoder import SmartGeocoder, AmbiguousResult, GeocodingException
from ebpub.geocoder.parser.parsing import normalize
from ebpub.geoadmin import OBMapField
from ebpub.geoadmin import OSMModelAdmin

import logging
from StringIO import StringIO



logger = logging.getLogger('ebpub.streets.admin')


class PlaceAdminForm(forms.ModelForm):
    class Meta:
        model = Place

    location = OBMapField(options={'isCollection': False, 'geometry': 'point'},
                          required=False)
    address = forms.CharField(max_length=255, required=False, 
                              help_text="""Address is optional and used to compute map point when no point is specified. Click 'Delete all Features' to remove current point.""")

    def _append_error(self, field, err):
        if not field in self._errors: 
            self._errors[field] = forms.util.ErrorList()
        self._errors[field].append(err)

    def clean(self):
        loc_info = self.cleaned_data.get('location')
        if isinstance(loc_info, list):
            # olwidget wraps geometries up as lists in case there's several per map
            assert len(loc_info) == 1
            loc_info = loc_info[0]
        if not loc_info:
            address = self.cleaned_data.get('address')
            if not address: 
                self._append_error('location', u'Either an address or a location must be specified.')
            else:
                # try to geocode the address...
                try:
                    geocoder = SmartGeocoder()
                    addr = geocoder.geocode(address) 
                    loc_info = addr['point']
                except AmbiguousResult:
                    self._append_error('location', u'Address is ambiguous, please specify a point directly.')
                except GeocodingException:
                    self._append_error('location', u'Unable to geocode address, please correct the address or specify a point directly.')
            # Again, olwidget expects these to be lists...
            loc_info = [loc_info]
            self.cleaned_data['location'] = loc_info
        return super(PlaceAdminForm, self).clean()

    def save(self, *args, **kwargs):
        # update normalized name
        self.instance.normalized_name = normalize(self.instance.pretty_name)
        return super(PlaceAdminForm, self).save(*args, **kwargs)

class PlaceImportForm(forms.Form):
    place_type = forms.ModelChoiceField(queryset=PlaceType.objects.all())
    csv_file = forms.FileField(
        required=True,
        help_text='These fields are required for each row: pretty_name, address, lat, lon, &lt;synonym&gt;, &lt;synonym&gt;, ...')


class PlaceExportForm(forms.Form):
    place_type = forms.ModelChoiceField(
        queryset=PlaceType.objects.all(),
        help_text='These fields will be exported in each row: pretty_name, address, lat, lon, &lt;synonym&gt;, &lt;synonym&gt;, ...')


class PlaceAdmin(OSMModelAdmin):
    list_display = ('pretty_name', 'place_type', 'address',)
    list_filter  = ('place_type',)
    search_fields = ('pretty_name', 'address', 'place_type__name')
    fields = ('pretty_name', 'place_type', 'url', 'address', 'location')
    form = PlaceAdminForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        """
        # Hack around django bug https://code.djangoproject.com/ticket/16110 :
        # there's no decent way to allow GeometryField(blank=True, null=False)
        # - i.e. required in the database but not required by a form.
        # We have to override the widget with *both* required=False and null=False.
        # The form's clean() method will attempt to fix it by geocoding.
        if db_field.name == 'location':
            kwargs['required'] = False
            kwargs['null'] = True
        return super(OSMModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def get_urls(self):
         urls = super(OSMModelAdmin, self).get_urls()
         my_urls = patterns('',
             url(r'^import/csv$', self.admin_site.admin_view(self.import_csv_view), name="streets_place_import_csv"),
             url(r'^export/csv$', self.admin_site.admin_view(self.export_csv_view), name="streets_place_export_csv")
         )
         return my_urls + urls
    
    def export_csv_view(self, request):

        if request.method == 'GET':
            export_form = PlaceExportForm()
        elif request.method == 'POST':
            export_form = PlaceExportForm(request.POST)

        if not export_form.is_bound or not export_form.is_valid(): 
            return self._show_export_csv_form(request, export_form)
            
        # ... do export csv
        # fields: pretty_name, address, lat, lon, url, <synonym>, <synonym>, ...
        place_type = export_form.cleaned_data['place_type']
        data = StringIO()
        serializer = csv.writer(data)
        for place in Place.objects.filter(place_type=place_type).all():
            row = [place.pretty_name, place.address or '', place.location.y, place.location.x, place.url or '']
            for synonym in PlaceSynonym.objects.filter(place=place).all():
                row.append(synonym.pretty_name)
            serializer.writerow(row)
        
        response = HttpResponse(data.getvalue(), mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % place_type.slug
        response['Cache-Control'] = 'no-cache'
        return response


    def import_csv_view(self, request):
        if not self.has_add_permission(request):
            raise PermissionDenied

        if request.method == 'GET':
            import_form = PlaceImportForm()
        if request.method == 'POST': 
            import_form = PlaceImportForm(request.POST, request.FILES)

        if not import_form.is_bound or not import_form.is_valid():
            return self._show_import_csv_form(request, import_form)

        # csv fields: 
        # pretty_name, address, lat, lon, url, <synonym>, <synonym>, ...

        context = dict(
            errors = [],
            actions_taken = [],
        )

        validated_rows = []

        place_type = import_form.cleaned_data['place_type']
        try:
            csvfile = import_form.cleaned_data['csv_file']
            rows = csv.reader(csvfile)
        except:
            message = "Unable to read the specified CSV file"
            context['errors'].append(message)
            return self._show_import_csv_results(request, context)

        try:
            for row in rows:
                if len(row) < 2:
                    message = "Line %d: Missing required fields." % rows.line_num
                    context['errors'].append(message)
                    continue
                
                synonyms = []
                point = None
                place_url = ''

                pretty_name, address = [x.strip() for x in row[0:2]]
                if pretty_name ==  '': 
                    message = "Line %d: Empty name" % rows.line_num
                    context['errors'].append(message)
                    continue

                if len(row) > 2:
                    try:
                        lat, lon  = row[2:4]
                        if lat != '' or lon != '':
                            lat = float(lat.strip())
                            lon = float(lon.strip())
                            point = geos.Point(lon, lat)
                            if len(row) > 4:
                                place_url = row[4]
                                synonyms = [x.strip() for x in row[5:]]
                    except ValueError: 
                        message = 'Line %d "%s": Invalid lat, lon' % (rows.line_num, pretty_name)
                        context['errors'].append(message)
                        continue

                
                if point is None:
                    if address == '':
                        message = 'Line %d "%s": Address and lat,lon are both empty.' % (rows.line_num, pretty_name)
                        context['errors'].append(message)
                        continue

                    # try to geocode the address
                    try:
                        geocoder = SmartGeocoder()
                        addr = geocoder.geocode(address) 
                        point = addr['point']
                    except AmbiguousResult:
                        message = 'Line %d "%s": Address "%s" is ambiguous, please specify a point directly.' % (rows.line_num, pretty_name, address)
                        context['errors'].append(message)
                        continue
                    except GeocodingException:
                        message = 'Line %d "%s": Unable to geocode address "%s", please correct the address or specify a point directly.' % (rows.line_num, pretty_name, address)
                        context['errors'].append(message)
                        continue
                
                # phew!
                validated_rows.append([pretty_name, address, point, place_url, synonyms])

        except csv.Error, e:
            message = "Stopped on line %d: %s" % (rows.line_num, e)
            context['errors'].append(message)
            return self._show_import_csv_results(request, context)
        except Exception, e:
            message = "Stopped on line %d: %s" % (rows.line_num, e)
            context['errors'].append(message)
            return self._show_import_csv_results(request, context)
        
        
        # wonderful, now do something...
        for pretty_name, address, point, place_url, synonyms in validated_rows: 
            normalized_name = normalize(pretty_name)
            
            try: 
                place = Place.objects.get(normalized_name=normalized_name,
                                          location__distance_lte=(point, D(m=1)))
                created = False
            except Place.DoesNotExist:
                place = Place(normalized_name=normalized_name)
                created = True
            
            try:
                place.pretty_name = pretty_name
                place.address = address
                place.location = point
                place.url = place_url
                place.place_type = place_type
                place.save()

                if created: 
                    message = 'Created new place %s' % (pretty_name)
                else: 
                    message = 'Updated place %s' % (pretty_name)
                context['actions_taken'].append(message)
            except: 
                log_exception()
                message = 'Error adding place "%s"' % pretty_name
                context['errors'].append(message)
                continue

                
            # now update Synonyms

            # destroy synonyms not in the new list, identify new synonyms
            new_synonyms = set(synonyms)
            for synonym in PlaceSynonym.objects.filter(place=place).all():
                if synonym.pretty_name not in new_synonyms:
                    synonym.delete()
                    message = 'Removing old synonym "%s" for "%s"' % (synonym.pretty_name, pretty_name)
                    context['actions_taken'].append(message)
                else:
                    # seen it in the database, don't make a new one
                    new_synonyms.remove(synonym.pretty_name)
                    message = 'Keeping synonym "%s" for "%s"' % (synonym.pretty_name, pretty_name)
                    context['actions_taken'].append(message)

            for synonym in new_synonyms:
                try:
                    ns = PlaceSynonym(pretty_name=synonym,
                                      normalized_name=normalize(synonym),
                                      place=place)
                    ns.save()
                    message = 'Created new synonym "%s" for "%s"' % (synonym, pretty_name)
                    context['actions_taken'].append(message)
                except:
                    message = 'Unable to add synonym "%s" for "%s"' % (synonym, pretty_name)
                    context['errors'].append(message)

            
            
        return self._show_import_csv_results(request, context)
        
        
    def _show_import_csv_results(self, request, context):
        return self._render_admin_template('admin/streets/place/import_places_csv_result.html',
                                           request, context)
        

    def _show_import_csv_form(self, request, import_form):
        opts = self.model._meta
        adminform = helpers.AdminForm(import_form, [(None, {'fields': import_form.base_fields.keys()})], {})
        context = {
            'title': 'Import %s' % force_unicode(opts.verbose_name_plural),
        }
        return self._render_admin_template('admin/streets/place/import_places_csv.html',
                                           request, context, import_form)


    def _show_export_csv_form(self, request, export_form):
        opts = self.model._meta
        context = {
           'title': 'Export %s' % force_unicode(opts.verbose_name_plural),
        }
        return self._render_admin_template('admin/streets/place/export_places_csv.html',
                                           request, context, export_form)

    
    def _render_admin_template(self, template_name, request, context, form=None):
        # try to wrap and jump through as many hoops as have a determinable shape... 
        
        opts = self.model._meta        
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        ctx = {
            'is_popup': request.REQUEST.has_key('_popup'),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
            'opts': opts,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request),
            'has_delete_permission': self.has_delete_permission(request),
        }
        
        if form is not None: 
            adminform = helpers.AdminForm(form, [(None, {'fields': form.base_fields.keys()})], {})
            ctx['errors'] = helpers.AdminErrorList(form, [])
            ctx['adminform'] = adminform

        ctx.update(context)

        return render_to_response(template_name, ctx, context_instance=context_instance)


class BlockAdmin(OSMModelAdmin):

    list_display = ('pretty_name', 'street', 'suffix', 'left_zip', 'right_zip', 'left_city', 'right_city')
    list_filter = ('suffix', 'left_city', 'right_city', 'left_zip', 'right_zip')
    search_fields = ('pretty_name',)
    readonly_fields = ('from_num', 'to_num',)

    fieldsets = (
        ('Name', {
                'fields': ('street_slug', 'pretty_name', 'street_pretty_name',
                           'predir', 'street', 'suffix', 'postdir',
                           )
                }),
        ('Address Ranges', {
                'fields': ('left_from_num', 'left_to_num',
                           'right_from_num', 'right_to_num',
                           'from_num', 'to_num'),
                'description': 'Addresses on this block. At least one must be provided; the rest will be guessed if necessary. Order will be fixed if you get it backwards.'
                }),
        ('Location', {
                'fields': ('left_zip', 'right_zip', 'left_city', 'right_city',
                           'left_state', 'right_state',
                           'parent_id',
                           'geom',
                           )
                })
        )


class PlaceTypeAdmin(OSMModelAdmin):
    list_display = ('name', 'slug', 'is_geocodable', 'is_mappable')
    search_fields = ('name',)


class StreetAdmin(OSMModelAdmin):
    list_display = ('pretty_name', 'suffix', 'city', 'state',)
    list_filter = ('suffix', 'city', 'state',)
    search_fields = ('pretty_name',)
    readonly_fields = ('street',)
    prepopulated_fields = {'street_slug': ('pretty_name',)}

class BlockIntersectionAdmin(OSMModelAdmin):
    list_display = ('block', 'intersecting_block', 'intersection',)
    raw_id_fields = ('block', 'intersecting_block', 'intersection',)
    search_fields = ('block__pretty_name',)

class IntersectionAdmin(OSMModelAdmin):
    list_display = ('pretty_name', 'zip', 'city', 'state')
    list_filter = ('zip', 'city', 'state')
    search_fields = ('pretty_name',)

class SuburbAdmin(OSMModelAdmin):
    pass

class StreetMisspellingAdmin(OSMModelAdmin):
    list_display = ('incorrect', 'correct',)
    search_fields = ('incorrect', 'correct',)

class PlaceSynonymAdmin(OSMModelAdmin):
    list_display = ('pretty_name', 'place')
    search_fields = ('pretty_name', 'place')
    readonly_fields = ('normalized_name',)

# Hack to ensure that the templates in obadmin get used, if it's installed
# and the relevant template exists.
# This is because olwidget defines its own olwidget_change_list.html
# template for GeoModelAdmin, which OSMModelAdmin inherits.
try:
    import obadmin.admin
    BlockAdmin.change_list_template = 'admin/streets/block/change_list.html'
    PlaceAdmin.change_list_template = 'admin/streets/place/change_list.html'
except ImportError:
    pass

admin.site.register(Block, BlockAdmin)
admin.site.register(Street, StreetAdmin)
admin.site.register(BlockIntersection, BlockIntersectionAdmin)
admin.site.register(Intersection, IntersectionAdmin)
admin.site.register(Suburb, SuburbAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(PlaceType, PlaceTypeAdmin)
admin.site.register(PlaceSynonym, PlaceSynonymAdmin)
admin.site.register(StreetMisspelling, StreetMisspellingAdmin)

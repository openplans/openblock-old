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

from django.contrib import admin
from django import forms
from ebpub.streets.models import Block, Street, BlockIntersection, \
    Intersection, Suburb, Place, PlaceSynonym, StreetMisspelling
from ebpub.geocoder import SmartGeocoder, AmbiguousResult, GeocodingException
from ebpub.geocoder.parser.parsing import normalize
from ebpub.geoadmin import OBMapField
from ebpub.geoadmin import OSMModelAdmin

import logging

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

class PlaceAdmin(OSMModelAdmin):
    list_display = ('pretty_name', 'address',)
    search_fields = ('pretty_name',)
    fields = ('pretty_name', 'address', 'location')

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


class StreetAdmin(OSMModelAdmin):
    list_display = ('pretty_name', 'suffix', 'city', 'state',)
    list_filter = ('suffix', 'city', 'state',)
    search_fields = ('pretty_name',)

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

admin.site.register(Block, BlockAdmin)
admin.site.register(Street, StreetAdmin)
admin.site.register(BlockIntersection, BlockIntersectionAdmin)
admin.site.register(Intersection, IntersectionAdmin)
admin.site.register(Suburb, SuburbAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(PlaceSynonym, PlaceSynonymAdmin)
admin.site.register(StreetMisspelling, StreetMisspellingAdmin)

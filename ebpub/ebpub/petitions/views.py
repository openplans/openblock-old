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

from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from ebpub.metros.allmetros import get_metro
from ebpub.petitions.models import Petition, Petitioner
from ebpub.streets.utils import full_geocode
from ebpub.utils.view_utils import eb_render
import datetime

class LocationField(forms.CharField):
    def clean(self, value):
        if not value:
            raise forms.ValidationError('Enter your location.')
        try:
            result = full_geocode(value, search_places=False)
        except Exception:
            raise forms.ValidationError("We're not familiar with this location. Could you please enter another one that we'd know, like a ZIP code, perhaps?")
        if result['ambiguous'] and result['type'] != 'block':
            raise forms.ValidationError("This location is ambiguous. Please enter one of the following: %s" % ', '.join([r['address'] for r in result['result']]))
        return value

class PetitionForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size': 30}))
    location = LocationField(max_length=100, widget=forms.TextInput(attrs={'size': 30}))
    city = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'size': 30}), initial=get_metro()['city_name'])
    state = forms.CharField(max_length=2, widget=forms.TextInput(attrs={'size': 2}), initial=get_metro()['state'])
    email = forms.EmailField(widget=forms.TextInput(attrs={'size': 30}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 35, 'rows': 4}))

def form_view(request, slug, is_schema):
    if is_schema:
        p = get_object_or_404(Petition, schema__slug=slug)
    else:
        p = get_object_or_404(Petition, slug=slug)
    if request.method == 'POST':
        form = PetitionForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR', '')
            Petitioner.objects.create(
                petition=p,
                name=cd['name'].strip(),
                location=cd['location'].strip(),
                city=cd['city'].strip(),
                state=cd['state'].strip(),
                email=cd['email'].strip().lower(),
                notes=cd['notes'].strip(),
                date_signed=datetime.datetime.now(),
                ip_address=ip_address,
            )
            return HttpResponseRedirect('thanks/')
    else:
        form = PetitionForm()
    return eb_render(request, 'petitions/form.html', {'form': form, 'is_schema': is_schema, 'petition': p})

def form_thanks(request, slug, is_schema):
    if is_schema:
        p = get_object_or_404(Petition.objects.select_related(), schema__slug=slug)
    else:
        p = get_object_or_404(Petition, slug=slug)
    return eb_render(request, 'petitions/thanks.html', {'is_schema': is_schema, 'petition': p})

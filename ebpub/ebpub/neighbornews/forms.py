#   Copyright 2011 OpenPlans, and contributors
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

class NewsItemForm(forms.Form):

    def clean(self):
        data = self.cleaned_data

        lat = data.get("latitude", None)
        lon = data.get("longitude", None)

        if lat is None and lon is None:
            raise forms.ValidationError("Please specify a location on the map.")

        return data

class NeighborMessageForm(NewsItemForm):
    title = forms.CharField(max_length=255, label="Title")
    location_name = forms.CharField(max_length=255, label="Address or Location",
                                    required=False)
    url = forms.CharField(max_length=2048, label="Link to more information",
                          required=False)
    image_url = forms.CharField(max_length=2048, label="Link to image",
                                required=False)
    categories = forms.CharField(max_length=10240, required=False,
                                 help_text="Separate with commas")
    description = forms.CharField(max_length=10240, label="Message",
                                  widget=forms.Textarea)
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)


class NeighborEventForm(NewsItemForm):
    title = forms.CharField(max_length=255, label="Title")
    location_name = forms.CharField(max_length=255, label="Address or Location",
                                    required=False)
    item_date = forms.DateField(label="Date")
    start_time = forms.TimeField(label="Start Time", required=False,
                                 input_formats=("%I:%M%p",))
    end_time = forms.TimeField(label="End Time", required=False,
                               input_formats=("%I:%M%p",))
    url = forms.CharField(max_length=2048, label="Link to more information",
                          required=False)
    image_url = forms.CharField(max_length=2048, label="Link to image", required=False)
    categories = forms.CharField(max_length=10240, required=False,
                                 help_text="Separate with commas")
    description = forms.CharField(max_length=10240, label="Message",
                                  widget=forms.Textarea)
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)

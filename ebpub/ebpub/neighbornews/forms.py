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
from ebpub.db.forms import NewsItemForm as NewsItemFormBase
from ebpub.db.models import NewsItem

class NewsItemForm(NewsItemFormBase):

    def clean(self):
        cleaned_data = super(NewsItemForm, self).clean()
        # Note, any NewsItem fields that aren't listed in self._meta.fields
        # have to be manually saved here, because that's the list that's
        # normally consulted when setting attributes on the instance.
        for key in forms.fields_for_model(self._meta.model):
            if key in cleaned_data.keys():
                setattr(self.instance, key, cleaned_data[key])
        return cleaned_data

class NeighborMessageForm(NewsItemForm):

    class Meta:
        model = NewsItem
        # Hide some fields.
        fields = ('title', 'location_name', 'url', 'description',
                  'image_url', 'categories',
                  'description',
                  'location',
                  )

    location_name = forms.CharField(max_length=255, label="Address or Location",
                                    required=False)
    image_url = forms.CharField(max_length=2048, label="Link to image",
                                required=False)
    categories = forms.CharField(max_length=10240, required=False,
                                 help_text="Separate with commas")
    location = forms.CharField(max_length=255, widget=forms.HiddenInput)


class NeighborEventForm(NeighborMessageForm):

    class Meta:
        model = NewsItem
        # Hide some fields, re-order others.
        fields = ('title', 'location_name',
                  'item_date',
                  'start_time', 'end_time',
                  'url', 'image_url',
                  'categories',
                  'description',
                  )

    item_date = forms.DateField(label="Date")
    start_time = forms.TimeField(label="Start Time", required=False,
                                 input_formats=("%I:%M%p",))
    end_time = forms.TimeField(label="End Time", required=False,
                               input_formats=("%I:%M%p",))

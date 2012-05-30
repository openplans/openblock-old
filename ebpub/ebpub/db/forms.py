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

"""
Custom Forms for ebpub.db.models.
"""

from ebpub.db import models
from django import forms

class NewsItemForm(forms.ModelForm):
    class Meta:
        model = models.NewsItem

    # This one is a m2m field with a 'through' model, so you can't
    # assign to it directly.
    exclude = ('location_set',)

    url = forms.URLField(widget=forms.TextInput(attrs={'size': 80}), required=False)

    def clean(self):
        # Remove this from cleaned_data, otherwise form.save() will
        # try to assign it, even if it's in self.exclude ... and
        # that's an error since it has a 'through' model.  Seems odd,
        # maybe django should check the exclude list? shrug.
        self.cleaned_data.pop('location_set', None)
        return self.cleaned_data

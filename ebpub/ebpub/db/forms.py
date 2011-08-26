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

from ebpub.db import models
from django import forms

class NewsItemForm(forms.ModelForm):
    class Meta:
        model = models.NewsItem

    url = forms.URLField(widget=forms.TextInput(attrs={'size': 80}), required=False)

# these values map to the Attribute field names
FIELD_TYPE_CHOICES=(
    ('varchar',  'Character'),
    ('int',      'Integer'),
    ('date',     'Date'),
    ('time',     'Time'),
    ('datetime', 'DateTime'),
    ('bool',     'Boolean'),
    ('text',     'Text'),
    ('', 'Lookup (single)'),
    ('', 'Lookup (many-to-many)'),
)

class SchemaFieldInlineOnSchemaForm(forms.ModelForm):
    class Meta:
        model = models.SchemaField

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs: # eg. if this is a 'change' rather than 'add'
            # Transform the real_name column ('varchar01') from the model into
            # human field_type ('Character') for the form.
            initial = kwargs.get('initial', {})
            initial['field_type'] = kwargs['instance'].real_name[0:-2]

            kwargs['initial'] = initial
        super(forms.ModelForm, self).__init__(*args, **kwargs)

    # List form fields that need to be customized/created from the default
    field_type = forms.ChoiceField(
        label="Field Type",
        required=True,
        choices=FIELD_TYPE_CHOICES,
        initial='text',
    )

    def save(self, commit=True):
        instance = super(forms.ModelForm, self).save(commit)

        # Transform form field_type back into model real_name
        # find next open real_name to assign to
        if instance.pk is None:
          field_type = self.cleaned_data['field_type']
          instance.real_name = determine_next_real_name('field_type')
        else:
            # this should move to a form custom validation
            # which should also check that determine_next_real_name doesn't fail
            raise "Can't change field_type, would require migrating all previous Attributes"

        return instance

    # helper method for real_name presentation
    def determine_next_real_name(field_type):
        in_use = 0
        instance = super(forms.ModelForm, self).save(commit)
        # count how many of this field_type are in use
        for field in instance.schema.schemafield_set.all():
            if field.real_name[0:len(field_type)]:
                in_use += 1
        # generate the next real_name for this field_type
        real_name = "%s%02d" % (field_type, in_use - 1)
        # check that the field exists (less error-prone than this code knowing
        # there can be five varchars, two times, four datetimes...)
        if real_name in models.Attribute._meta.get_all_field_names():
            return real_name
        else:
            return False

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
        initial='character',
    )

    # Can't just set this as ModelAdmin.readonly_fields because then
    # it's not actually an input so the value doesn't end up in
    # cleaned_data, and we need it.
    real_name = forms.CharField(required=False, label='real_name (Attributes column)',
                                initial='(none)',
                                widget=forms.TextInput(attrs={'readonly': 'readonly',
                                                              'style': 'border: none'}))

    def clean(self, commit=True):

        if self.is_bound and self.instance.pk:
            # On edits, make sure we don't change real_name.
            # TODO: it's allowed iff there are no NewsItems with this schema?
            if self.instance.real_name != self.cleaned_data['real_name']:
                raise forms.ValidationError(
                    "Can't change field_type, would require migrating all existing NewsItems' Attributes")
            return self.cleaned_data
        else:
            # On creation, derive real_name from the chosen field type.
            field_type = self.cleaned_data['field_type']
            self.cleaned_data['real_name'] = self.determine_next_real_name(field_type)
            return self.cleaned_data

    def determine_next_real_name(self, field_type):
        """
        Given a field_type, find the next available real_name we can use.
        """
        # Count how many of this field_type are in use.
        in_use = 0
        for field in models.SchemaField.objects.filter(schema=self.cleaned_data['schema']):
            if field.real_name[:len(field_type)] == field_type:
                in_use += 1
        # generate the next real_name for this field_type
        real_name = "%s%02d" % (field_type, in_use + 1)
        if models.SchemaField.objects.filter(schema=self.cleaned_data['schema'],
                                             real_name=real_name).count():
            raise forms.ValidationError(
                "There is already a SchemaField with real_name=%r." % real_name)
            # TODO: could check if there is a lower number available?

        # Check that the field exists (less error-prone than this code knowing
        # there can be five varchars, two times, four datetimes...)
        if real_name in models.Attribute._meta.get_all_field_names():
            return real_name
        else:
            raise forms.ValidationError(
                "We can't store any more SchemaFields of type %s" % field_type)

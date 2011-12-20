#   Copyright 2011 OpenPlans and contributors
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

from django.contrib.gis import admin
from ebpub.geoadmin import OSMModelAdmin
from .models import NewsItemFlag

from django.forms.widgets import Input, MultiWidget
from django.utils.safestring import mark_safe

from django import forms

class SubmitInput(Input):
    input_type = 'submit'

APPROVE=u'approve item'
REJECT=u'delete item'

class ModerationWidget(MultiWidget):

    # Two buttons whose output is a single string.
    # There's probably a cleaner/shorter way to do this?

    def __init__(self, attrs=None):
        widgets=[SubmitInput(attrs={'value': APPROVE}),
                 SubmitInput(attrs={'value': REJECT})]
        MultiWidget.__init__(self, widgets, attrs=attrs)

    def decompress(self, value):
        # We don't actually care about this, but get
        # NotImplementedError without it.
        return [value, value]

    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), returns a Unicode string
        representing the HTML for the whole lot.

        This hook allows you to format the HTML design of the widgets, if
        needed.
        """
        return u'&nbsp;'.join(rendered_widgets)

    def value_from_datadict(self, data, files, name):
        result = MultiWidget.value_from_datadict(self, data, files, name)
        # What we have is a list of the strings that were submitted to
        # our sub-widgets and Nones for the others.
        # Since input is destined for a single CharField, merge it.
        result = u' '.join([s for s in result if s])
        return result

class ModerationForm(forms.ModelForm):
    class Meta:
        model = NewsItemFlag

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ModerationForm, self).__init__(*args, **kwargs)

    moderate = forms.CharField(widget=ModerationWidget(), required=False)

    def clean(self):
        moderation = self.cleaned_data.get('moderate')
        if moderation == APPROVE:
            self.cleaned_data['state'] = u'approved'
        elif moderation == REJECT:
            self.cleaned_data['state'] = u'deleted'
            if self.instance:
                item = self.instance.news_item
                if item is not None:
                    msg = u'Deleted news item %d' % item.id
                    item.delete()
                    # XXX self.instance will get auto-deleted anyway
                    # XXX can i somehow trigger a redirect?? argh i don't
                    # have a response and we don't have redirects as exceptions!
                    self.instance.news_item = None
                    if self.request is not None:
                        from django.contrib import messages
                        messages.add_message(self.request, messages.INFO, msg)


class NewsItemFlagAdmin(OSMModelAdmin):

    form = ModerationForm

    def get_form(self, request, obj=None, **kwargs):
        # Jumping through hoops to make request available
        # to the form instance, so it can be accessed during clean().
        # See eg http://stackoverflow.com/questions/1057252/django-how-do-i-access-the-request-object-or-any-other-variable-in-a-forms-cle
        _base = super(NewsItemFlagAdmin, self).get_form(request, obj, **kwargs)
        class ModelFormMetaClass(_base):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return _base(*args, **kwargs)
        return ModelFormMetaClass

    list_display = ('item_title', 'item_schema', 'state', 'reason', 'submitted', 'updated')
    search_fields = ('item_title', 'item_description', 'comment',)

    list_filter = ('reason', 'state', 'news_item__schema__slug',)
    # XXX TODO: Allow deleting the NewsItem directly from our form.

    raw_id_fields = ('news_item',)

    date_hierarchy = 'submitted'
    readonly_fields = ('item_title', 'item_schema', 'item_description', 'item_url',
                       'item_pub_date',
                       'submitted',
                       )

admin.site.register(NewsItemFlag, NewsItemFlagAdmin)

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

from .models import NewsItemFlag
from django import forms
from django.conf.urls.defaults import patterns, url
from django.contrib import messages
from django.contrib.gis import admin
from django.forms.widgets import Widget
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from ebpub.geoadmin import OSMModelAdmin


class ModerationWidget(Widget):

    instance = None  # Gets bound at widget init time.

    def render(self, name, value, attrs=None):
        # TODO: this is OK, but if the instance isn't saved yet, I'd
        # like to totally hide the widget label too.
        if self.instance and self.instance.pk is not None:
            output = u'''
        <a href="moderate/?delete=1" class="button">Delete News Item!</a>
        <a href="moderate/?approve=1" class="button">Approve it! (un-flag)</a>
'''
            return mark_safe(output)
        return u''

class ModerationForm(forms.ModelForm):
    class Meta:
        model = NewsItemFlag

    def __init__(self, *args, **kwargs):
        super(ModerationForm, self).__init__(*args, **kwargs)
        self.fields['moderate'].widget.instance = self.instance

    moderate = forms.CharField(widget=ModerationWidget(), required=False)


def bulk_delete_action(modeladmin, request, queryset):
    """
    Delete a batch of NewsItemFlags and their associated NewsItems.
    """
    # Admin bulk action as per
    # https://docs.djangoproject.com/en/1.3/ref/contrib/admin/actions/
    ids = [v['news_item_id'] for v in queryset.values('news_item_id')]
    queryset.delete()
    from ebpub.db.models import NewsItem
    NewsItem.objects.filter(id__in=ids).delete()
    messages.add_message(request, messages.INFO,
                         u'%d NewsItems, and all associated flags, deleted' % len(ids))

bulk_delete_action.short_description = u'Delete all selected News Items'

def bulk_approve_action(modeladmin, request, queryset):
    """
    Approve a batch of NewsItemFlags.
    """
    # Admin bulk action as per
    # https://docs.djangoproject.com/en/1.3/ref/contrib/admin/actions/
    queryset.update(state='approved')
    messages.add_message(request, messages.INFO, u'%d flagged items approved'
                         % queryset.count())

bulk_approve_action.short_description = u'Approve all selected NewsItems (un-flag)'


class NewsItemFlagAdmin(OSMModelAdmin):

    # We want new items first.
    ordering = ('-state', '-submitted')

    form = ModerationForm

    list_display = ('item_title', 'item_schema', 'state', 'reason', 'submitted', 'updated')
    search_fields = ('item_title', 'item_description', 'comment',)

    # TODO: filtering on news_item__schema__slug gives the filter the label 'slug',
    # which is not very user-friendly.  Don't see any way around that?
    list_filter = ('reason', 'state', 'news_item__schema__slug',)

    raw_id_fields = ('news_item',)

    date_hierarchy = 'submitted'
    readonly_fields = (
        'state',
        'submitted', 'updated',
        'view_item',
        'item_title', 'item_schema', 'item_description', 'item_original_url',
        'item_pub_date',
        )

    fieldsets = (
        (None, {'fields': ('moderate',
                           'reason',
                           'news_item',
                           'comment',
                           'state',
                           'submitted', 'updated',
                          )
                }),
        ('NewsItem info', {'fields': readonly_fields[3:]}),
        )

    actions = [bulk_approve_action, bulk_delete_action]

    def get_urls(self):
        urls = patterns(
            '',
            url(r'^(.+)/moderate/$', self.admin_site.admin_view(self.handle_moderation)),
            )
        urls = urls + super(NewsItemFlagAdmin, self).get_urls()
        return urls

    def handle_moderation(self, request, object_id):
        """
        View to delete or approve a single flagged item.
        """
        deleting = request.REQUEST.get('delete')
        approving = request.REQUEST.get('approve')
        qs = self.form.Meta.model.objects.filter(id=object_id)
        if request.method == 'GET':
            context = RequestContext(request,
                                     {'deleting': deleting, 'approving': approving,})
            return render_to_response('moderation/moderate_confirmation.html', context)
        elif request.method == 'POST':
            if deleting:
                bulk_delete_action(self, request, qs)
            elif approving:
                bulk_approve_action(self, request, qs)
        return HttpResponseRedirect('../../')

admin.site.register(NewsItemFlag, NewsItemFlagAdmin)

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

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from ebpub.accounts.models import User
from ebpub.accounts.utils import login_required
from ebpub.db.models import Schema, SchemaField, Lookup, NewsItem
from ebpub.neighbornews.forms import NeighborMessageForm, NeighborEventForm
from ebpub.neighbornews.models import NewsItemCreator
from ebpub.neighbornews.utils import NEIGHBOR_MESSAGE_SLUG, NEIGHBOR_EVENT_SLUG
from ebpub.neighbornews.utils import if_disabled404, can_edit
from ebpub.utils.view_utils import eb_render
import re

@if_disabled404(NEIGHBOR_MESSAGE_SLUG)
@login_required
@csrf_protect
def new_message(request):
    """
    Add form for neighbor-messages
    """
    schema = Schema.objects.get(slug=NEIGHBOR_MESSAGE_SLUG)
    FormType = NeighborMessageForm
    return _new_item(request, schema, FormType)


@if_disabled404(NEIGHBOR_EVENT_SLUG)
@login_required
@csrf_protect
def new_event(request):
    """
    Add form for neighbor-events
    """
    schema = Schema.objects.get(slug=NEIGHBOR_EVENT_SLUG)
    FormType = NeighborEventForm
    return _new_item(request, schema, FormType)


@if_disabled404(NEIGHBOR_MESSAGE_SLUG)
@login_required
@csrf_protect
@can_edit
def edit_message(request, newsitem):
    """
    Edit form for neighbor-messages
    """
    FormType = NeighborMessageForm
    return _edit_item(request, newsitem, FormType)

@if_disabled404(NEIGHBOR_EVENT_SLUG)
@login_required
@csrf_protect
@can_edit
def edit_event(request, newsitem):
    """
    Edit form for neighbor-events
    """
    FormType = NeighborEventForm
    return _edit_item(request, newsitem, FormType)


@if_disabled404(NEIGHBOR_MESSAGE_SLUG)
@login_required
@csrf_protect
@can_edit
def delete_message(request, newsitem):
    """
    Delete confirmation for neighbor-messages
    """
    return _delete(request, newsitem)

@if_disabled404(NEIGHBOR_EVENT_SLUG)
@login_required
@csrf_protect
@can_edit
def delete_event(request, newsitem):
    """
    Delete confirmation for neighbor-events
    """
    return _delete(request, newsitem)


def news_by_user(request, userid):
    """
    List of all messages / events posted by the given user.
    """
    user = User.objects.get(id=userid)
    is_viewing_self = False
    if not request.user.is_anonymous():
        if user.id == request.user.id:
            is_viewing_self = True
    items_by_schema = []
    for slug in ('neighbor-messages', 'neighbor-events'):
        try:
            schema = Schema.objects.get(slug=slug)
        except Schema.DoesNotExist:
            continue
        items = NewsItemCreator.objects.filter(user__id=userid, news_item__schema=schema)
        items = items.select_related().order_by('-news_item__item_date')
        items = [item.news_item for item in items]
        items_by_schema.append({'schema': schema, 'items': items})

    context = {'items_by_schema': items_by_schema, 'user': user,
               'is_viewing_self': is_viewing_self}
    return eb_render(request, "neighbornews/news_by_user.html", context)


################################################################
# Utility functions.

def _delete(request, newsitem):
    item = get_object_or_404(NewsItem, id=newsitem)
    if request.method == 'POST':
        item.delete()
        messages.add_message(request, messages.INFO, 'Deleted.')
        return HttpResponseRedirect(reverse('neighbornews_by_user',
                                            args=(request.user.id,)))
    else:
        return eb_render(request, 'neighbornews/delete_form.html',
                         {'newsitem': item})

def _edit_item(request, newsitem_id, FormType):
    instance = NewsItem.objects.get(id=newsitem_id)
    if request.method == 'POST':
        form = FormType(request.POST, request.FILES, instance=instance)
    else:
        form = FormType(instance=instance)
    return _update_item(request, form, instance.schema, action='edit')


def _new_item(request, schema, FormType):
    if request.method == 'POST':
        form = FormType(request.POST, request.FILES)
    else:
        form = FormType()
    return _update_item(request, form, schema, action='create')


def _update_item(request, form, schema, action):
    # Do we need to use need captcha? 
    # This might depend on the request, so you can set it to a callable,
    # or rather a path to a callable.
    need_captcha = getattr(settings, 'NEIGHBORNEWS_USE_CAPTCHA', False)
    if isinstance(need_captcha, basestring):
        module, func = need_captcha.split(':')
        import importlib
        module = importlib.import_module(module)
        need_captcha = getattr(module, func)

    if callable(need_captcha):
        need_captcha = need_captcha(request)

    if need_captcha:
        form.need_captcha = True
        form.recaptcha_ip = request.META['REMOTE_ADDR']

    cat_field = SchemaField.objects.get(schema=schema, name='categories')
    if form.is_bound and form.is_valid():
        # Creating or updating a NewsItem.
        form.instance.schema = schema
        item = form.save()

        # Add a NewsItemCreator association; un-lazy the User.
        user = User.objects.get(id=request.user.id)
        NewsItemCreator.objects.get_or_create(news_item=item, user=user)

        # Image url.
        if form.cleaned_data['image_url'] is not None:
            item.attributes['image_url'] = form.cleaned_data['image_url']

        # Image.
        uploaded = form.cleaned_data['image']
        if uploaded is False:
            # This is apparently how File fields announce deletion. Is
            # that in the docs??
            item.newsitemimage_set.all().delete()
        elif uploaded:
            from ebpub.db.models import NewsItemImage
            # TODO: allow more than one? For now, we just delete and recreate.
            item.newsitemimage_set.all().delete()
            ni_image, created = NewsItemImage.objects.get_or_create(news_item=item,
                                                                    image=uploaded.name)
            ni_image.image.save(uploaded.name, uploaded)

        # Times.
        for key in ('start_time', 'end_time'):
            if key in form.fields and form.cleaned_data.get(key):
                item.attributes[key] = form.cleaned_data[key]

        # 'categories'
        cats = [cat.strip() for cat in form.cleaned_data['categories'].split(',') if cat.strip()]
        if len(cats):
            lookups = set()
            for cat in cats:
                code = _category_code(cat)
                nice_name = _category_nice_name(cat)
                try:
                    # We don't call get_or_create() yet because we
                    # only want to look up by the normalized code, to
                    # avoid dupes with slightly different names.
                    from django.db.models import Q
                    lu = Lookup.objects.filter(
                        Q(schema_field=cat_field),
                        Q(code=code) | Q(name=nice_name)
                        )[0]
                except (IndexError, Lookup.DoesNotExist):
                    # We know it doesn't exist, but use get_or_create_lookup()
                    # here b/c that takes care of the slug.
                    lu = Lookup.objects.get_or_create_lookup(cat_field, nice_name, code=code)
                lookups.add(lu.id)
            item.attributes['categories'] = ','.join(['%d' % luid for luid in lookups])

        detail_url = reverse('ebpub-newsitem-detail',
                             args=(schema.slug, '%d' % item.id))
        if action == 'create':
            messages.add_message(request, messages.INFO, '%s created.' % schema.name)
        else:
            messages.add_message(request, messages.INFO, '%s edited.' % schema.name)
        return HttpResponseRedirect(detail_url)

    elif form.instance:
        # Update form.
        if form.instance.attributes.get('categories'):
            cat_ids = form.instance.attributes['categories'].split(',')
            cat_lookups = Lookup.objects.filter(schema_field=cat_field, id__in=cat_ids)
            form.fields['categories'].initial = ', '.join(
                sorted([look.name for look in cat_lookups]))
        if form.instance.location:
            form.fields['location'].initial = form.instance.location.wkt

        existing_images = list(form.instance.newsitemimage_set.all())
        if existing_images:
            img = existing_images[0].image
            # TODO: allow uploading more than one?
            form.fields['image'].initial = img
        else:
            img = None

        for key in ('start_time', 'end_time', 'image_url'):
            if key in form.fields and form.instance.attributes.get(key):
                value = form.instance.attributes[key]
                if key.endswith('time'):
                    value = value.strftime('%H:%M%p')
                form.fields[key].initial = value

    mapconfig = {
        'locations': [],
        'layers': [],
        'baselayer_type': settings.MAP_BASELAYER_TYPE,

    }
    ctx = {
        'form': form,
        'map_configuration': mapconfig,
        'default_lon': settings.DEFAULT_MAP_CENTER_LON,
        'default_lat': settings.DEFAULT_MAP_CENTER_LAT,
        'default_zoom': settings.DEFAULT_MAP_ZOOM,
        'schema': schema,
        'action': action,
        'need_captcha': need_captcha,
        'image': img,
    }
    return eb_render(request, "neighbornews/new_message.html", ctx)


def _category_code(cat):
    code = cat.strip().lower()
    code = re.sub('\s+', ' ', code)
    code = re.sub('[^\w]', '-', code)
    return code

def _category_nice_name(cat):
    nice = cat.strip().title()
    nice = re.sub('\s+', ' ', nice)
    return nice

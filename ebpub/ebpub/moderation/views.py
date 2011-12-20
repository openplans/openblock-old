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

from .forms import NewsItemFlagForm
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from ebpub.db.models import NewsItem
from ebpub.utils.view_utils import eb_render

@csrf_protect
def newsitem_flag(request, newsitem_id):
    get_object_or_404(NewsItem.objects.by_request(request).values('id'), id=newsitem_id)
    if request.method == 'POST':
        form = NewsItemFlagForm(request.POST)
        if form.is_valid():
            form.save()
            return eb_render(request, 'moderation/flagged.html', {})

    else:
        form = NewsItemFlagForm()

    # Initial values are easier to set here since we have access to the request,
    # and the Form doesn't.
    form.fields['news_item'].initial = str(newsitem_id)
    if not request.user.is_anonymous():
        form.fields['user'].initial = request.user.email

    context = {
        'news_item_id': newsitem_id,
        'form': form,
        }
    return eb_render(request, 'moderation/flag_form.html', context)

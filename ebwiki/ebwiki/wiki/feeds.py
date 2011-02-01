#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebwiki
#
#   ebwiki is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebwiki is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebwiki.  If not, see <http://www.gnu.org/licenses/>.
#

from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from ebwiki.wiki.models import Page

class LatestEdits(Feed):
    title = "ebwiki"
    link = "/"
    subtitle = "Latest edits made to the ebwiki."
    title_template = "wiki/feeds/latest_title.html"
    description_template = "wiki/feeds/latest_description.html"

    feed_type = Atom1Feed

    def items(self):
        return Page.objects.order_by("-change_date")[:30]

    def item_link(self, item):
        return item.version_url()

    def item_author_name(self, item):
        return item.change_user

    def item_pubdate(self, item):
        return item.change_date

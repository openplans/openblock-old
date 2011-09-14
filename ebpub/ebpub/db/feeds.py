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

from django.contrib.syndication.views import Feed
from django.http import Http404
from django.utils.feedgenerator import Rss201rev2Feed
from ebpub.db.models import NewsItem, Location
from ebpub.db.utils import populate_attributes_if_needed, today
from ebpub.db.utils import make_search_buffer, url_to_block, BLOCK_RADIUS_CHOICES, BLOCK_RADIUS_DEFAULT
from ebpub.streets.models import Block
import datetime
import re

# RSS feeds powered by Django's syndication framework use MIME type
# 'application/rss+xml'. That's unacceptable to us, because that MIME type
# prompts users to download the feed in some browsers, which is confusing.
# Here, we set the MIME type so that it doesn't do that prompt.
class CorrectMimeTypeFeed(Rss201rev2Feed):
    mime_type = 'application/xml'

# This is a django.contrib.syndication.feeds.Feed subclass whose feed_type
# is set to our preferred MIME type.
class EbpubFeed(Feed):
    feed_type = CorrectMimeTypeFeed

location_re = re.compile(r'^([-_a-z0-9]{1,32})/([-_a-z0-9]{1,32})$')

def bunch_by_date_and_schema(newsitem_list, date_cutoff):
    current_schema_date, current_list = None, []
    for ni in newsitem_list:
        # Remove collapsable newsitems that shouldn't be published in the
        # feed yet. See the lengthy comment in AbstractLocationFeed.items().
        if ni.schema.can_collapse and ni.item_date >= date_cutoff:
            continue

        if current_schema_date != (ni.schema, ni.item_date):
            if current_list:
                yield current_list
            current_schema_date = (ni.schema, ni.item_date)
            current_list = [ni]
        else:
            current_list.append(ni)
    if current_list:
        yield current_list

class AbstractLocationFeed(EbpubFeed):
    "Abstract base class for location-specific RSS feeds."

    title_template = 'feeds/streets_title.html'
    description_template = 'feeds/streets_description.html'

    def items(self, obj):
        # Note that items() returns "packed" tuples instead of objects.
        # This is necessary because we return NewsItems and blog entries,
        # plus different types of NewsItems (bunched vs. unbunched).

        # Limit the feed to all NewsItems published in the last four days.
        # We *do* include items from today in this query, but we'll filter
        # those later in this method so that only today's *uncollapsed* items
        # (schema.can_collapse=False) will be included in the feed. We don't
        # want today's *collapsed* items to be included, because more items
        # might be added to the database before the day is finished, and
        # that would result in the RSS item being updated multiple times, which
        # is annoying.

        # TODO: re-use ebpub.db.schemafilters for filtering here.

        # TODO: allow user control over date range
        today_value = today()
        start_date = today_value - datetime.timedelta(days=5)
        # Include future stuff, useful for events
        end_date = today_value + datetime.timedelta(days=5)

        qs = NewsItem.objects.select_related().filter(
            schema__is_public=True,
            item_date__gte=start_date,
            item_date__lte=end_date).order_by('-item_date', 'schema__id', 'id')

        # Filter out ignored schemas -- those whose slugs are specified in
        # the "ignore" query-string parameter.
        if 'ignore' in self.request.GET:
            schema_slugs = self.request.GET['ignore'].split(',')
            qs = qs.exclude(schema__slug__in=schema_slugs)

        # Filter wanted schemas -- those whose slugs are specified in the
        # "only" query-string parameter.
        if 'only' in self.request.GET:
            schema_slugs = self.request.GET['only'].split(',')
            qs = qs.filter(schema__slug__in=schema_slugs)

        block_radius = self.request.GET.get('radius', BLOCK_RADIUS_DEFAULT)
        if block_radius not in BLOCK_RADIUS_CHOICES:
            raise Http404('Invalid radius')
        ni_list = list(self.newsitems_for_obj(obj, qs, block_radius))
        schema_list = list(set([ni.schema for ni in ni_list]))
        populate_attributes_if_needed(ni_list, schema_list)

        is_block = isinstance(obj, Block)

        # Note that this decorates the results by returning tuples instead of
        # NewsItems. This is necessary because we're bunching.
        for schema_group in bunch_by_date_and_schema(ni_list, today_value):
            schema = schema_group[0].schema
            if schema.can_collapse:
                yield ('newsitem', obj, schema, schema_group, is_block, block_radius)
            else:
                for newsitem in schema_group:
                    yield ('newsitem', obj, schema, newsitem, is_block, block_radius)

    def item_pubdate(self, item):
        if item[0] == 'newsitem':
            # Returning pub_date here because we need a datetime, not a date.
            # XXX That's potentially confusing since we use item_date elsewhere.
            # See ticket #77.
            if item[2].can_collapse:
                return item[3][0].pub_date
            return item[3].pub_date
        else:
            raise NotImplementedError()

    def item_link(self, item):
        if item[0] == 'newsitem':
            if item[2].can_collapse:
                return item[1].url() + '#%s-%s' % (item[3][0].schema.slug, item[3][0].item_date.strftime('%Y%m%d'))
            return item[3].item_url_with_domain()
        else:
            raise NotImplementedError()

    def newsitems_for_obj(self, obj, qs, block_radius):
        raise NotImplementedError('Subclasses must implement this.')


class BlockFeed(AbstractLocationFeed):

    def get_object(self, request, city_slug, street_slug, from_num, to_num,
                   predir, postdir):
        self.request = request
        return url_to_block(city_slug, street_slug, from_num, to_num, predir, postdir)

    def title(self, obj):
        return u"OpenBlock: %s" % obj.pretty_name

    def link(self, obj):
        return obj.url()

    def description(self, obj):
        return u"OpenBlock: %s" % obj.pretty_name

    def newsitems_for_obj(self, obj, qs, block_radius):
        search_buffer = make_search_buffer(obj.location.centroid, block_radius)
        return qs.filter(location__bboverlaps=search_buffer)


class LocationFeed(AbstractLocationFeed):

    def get_object(self, request, type_slug, slug):
        self.request = request
        return Location.objects.select_related().get(location_type__slug=type_slug,
                                                     slug=slug)

    def title(self, obj):
        return u"OpenBlock: %s" % obj.name

    def link(self, obj):
        return obj.url()

    def description(self, obj):
        return u"OpenBlock %s" % obj.name

    def newsitems_for_obj(self, obj, qs, block_radius):
        return qs.filter(newsitemlocation__location__id=obj.id)

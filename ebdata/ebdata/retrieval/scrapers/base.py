#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.db import transaction
from ebdata.retrieval import Retriever
from ebpub.db.models import NewsItem
from ebpub.geocoder import SmartGeocoder, GeocodingException, ParsingError, AmbiguousResult
from ebpub.utils.text import address_to_block

import datetime
import logging
import pytz
import traceback

local_tz = pytz.timezone(settings.TIME_ZONE)

class ScraperBroken(Exception):
    "Something changed in the underlying data format and broke the scraper."
    pass

class BaseScraper(object):
    """
    Base class for all scrapers in ebdata.retrieval.scrapers.
    """
    logname = 'basescraper'
    sleep = 0
    timeout = 20

    def __init__(self, use_cache=True):
        if not use_cache:
            self.retriever = Retriever(cache=None, sleep=self.sleep, timeout=self.timeout)
        else:
            self.retriever = Retriever(sleep=self.sleep, timeout=self.timeout)
        self.logger = logging.getLogger('eb.retrieval.%s' % self.logname)
        self.start_time = datetime.datetime.now()
        self._geocoder = SmartGeocoder()
        self.num_added = 0
        self.num_changed = 0

    def geocode(self, location_name, zipcode=None):
        """
        Tries to geocode the given location string, returning a Point object
        or None.
        """

        # Try to lookup the adress, if it is ambiguous, attempt to use
        # any provided zipcode information to resolve the ambiguity.
        # The zipcode is not included in the initial pass because it
        # is often too picky yeilding no results when there is a
        # legitimate nearby zipcode identified in either the address
        # or street number data.
        try:
            return self._geocoder.geocode(location_name)
        except AmbiguousResult as result: 
            # try to resolve based on zipcode...
            if zipcode is None: 
                self.logger.debug(
                    "Ambiguous results for address %s. (no zipcode to resolve dispute)" % 
                    (location_name, ))
                return None
            in_zip = [r for r in result.choices if r['zip'] == zipcode]
            if len(in_zip) == 0:
                self.logger.debug(
                    "Ambiguous results for address %s, but none in specified zipcode %s" % 
                    (location_name, zipcode))
                return None
            elif len(in_zip) > 1:
                self.logger.debug(
                    "Ambiguous results for address %s in zipcode %s, guessing first." % 
                    (location_name, zipcode))
                return in_zip[0]
            else:
                return in_zip[0]
        except (GeocodingException, ParsingError):
            self.logger.debug(
                "Could not geocode location: %s: %s" %
                (location_name, traceback.format_exc()))
            return None

    def update(self):
        'Run the scraper.'
        raise NotImplementedError()

    def fetch_data(self, *args, **kwargs):
        return self.retriever.fetch_data(*args, **kwargs)

    def get_html(self, *args, **kwargs):
        """An alias for fetch_data().
        For backward compatibility.
        """
        return self.fetch_data(*args, **kwargs)

    @classmethod
    def parse_html(cls, html):
        from lxml import etree
        from cStringIO import StringIO
        return etree.parse(StringIO(html), etree.HTMLParser())

    @transaction.commit_on_success
    def create_newsitem(self, attributes, **kwargs):
        """
        Creates and saves a NewsItem with the given kwargs. Returns the new
        NewsItem.

        kwargs MUST have the following keys:
            title
            item_date
            location_name
        For any other kwargs whose values aren't provided, this will use
        sensible defaults.
        
        kwargs MAY have the following keys: 
            zipcode - used to disambiguate geocoded locations

        kwargs may optionally contain a 'convert_to_block' boolean. If True,
        this will convert the given kwargs['location_name'] to a block level
        but will use the real (non-block-level) address for geocoding and Block
        association.

        attributes is a dictionary to use to populate this NewsItem's Attribute
        objects.
        """

        location = kwargs.get('location')
        location_name = kwargs.get('location_name')
        assert location or location_name, "At least one of location or location_name must be provided"
        if location is None:
            location = self.geocode(kwargs['location_name'], zipcode=kwargs.get('zipcode'))
            if location:
                location = location['point']
        if kwargs.pop('convert_to_block', False):
            kwargs['location_name'] = address_to_block(kwargs['location_name'])
            # If the exact address couldn't be geocoded, try using the
            # normalized location name.
            if location is None:
                location = self.geocode(kwargs['location_name'], zipcode=kwargs.get('zipcode'))
                if location:
                    location = location['point']

        # Normally we'd just use "schema = kwargs.get('schema', self.schema)",
        # but self.schema will be evaluated even if the key is found in
        # kwargs, which raises an error when using multiple schemas.
        schema = kwargs.get('schema', None) or self.schema

        ni = NewsItem.objects.create(
            schema=schema,
            title=kwargs['title'],
            description=kwargs.get('description', ''),
            url=kwargs.get('url', ''),
            pub_date=kwargs.get('pub_date', self.start_time),
            item_date=kwargs['item_date'],
            location=location,
            location_name=location_name,
            location_object=kwargs.get('location_object', None),
        )
        if attributes is not None:
            ni.attributes = attributes
        self.num_added += 1
        self.logger.info(u'Created NewsItem %s: %s (total created in this scrape: %s)', schema.slug, ni.id, self.num_added)
        return ni

    @transaction.commit_on_success
    def update_existing(self, newsitem, new_values, new_attributes):
        """
        Given an existing NewsItem and dictionaries new_values and
        new_attributes, determines which values and attributes have changed
        and saves the object and/or its attributes if necessary.
        """
        newsitem_updated = False
        # First, check the NewsItem's values.
        for k, v in new_values.items():
            if isinstance(v, datetime.datetime) and v.tzinfo is not None:
                # Django datetime fields are not timezone-aware, so we
                # can't compare them without stripping the zone.
                v = v.astimezone(local_tz).replace(tzinfo=None)
            if getattr(newsitem, k) != v:
                self.logger.debug('ID %s %s changed from %r to %r' % (newsitem.id, k, getattr(newsitem, k), v))
                setattr(newsitem, k, v)
                newsitem_updated = True
        if newsitem_updated:
            newsitem.save()
        else:
            self.logger.debug("No change to %s <%s>" % (newsitem.id, newsitem))
        # Next, check the NewsItem's attributes.
        for k, v in new_attributes.items():
            if isinstance(v, datetime.datetime) and v.tzinfo is not None:
                # Django datetime fields are not timezone-aware, so we
                # can't compare them without stripping the zone.
                v = v.astimezone(local_tz).replace(tzinfo=None)
            if newsitem.attributes.get(k) == v:
                continue
            elif k not in newsitem.attributes:
                self.logger.debug('ID %s %s was missing, setting to %r' %
                                 (newsitem.id, k, v))
            elif newsitem.attributes.get(k) != v:
                self.logger.debug('ID %s %s changed from %r to %r' %
                                 (newsitem.id, k, newsitem.attributes[k], v))
            newsitem.attributes[k] = v
            newsitem_updated = True
        if newsitem_updated:
            self.num_changed += 1
            self.logger.debug('Total changed in this scrape: %s', self.num_changed)
        else:
            self.logger.debug('No changes to NewsItem %s detected', newsitem.id)

    def create_or_update(self, old_record, attributes, **kwargs):
        """unified API for updating or creating a NewsItem.
        """
        if old_record:
            self.update_existing(old_record, kwargs, attributes or {})
        else:
            self.create_newsitem(attributes=attributes, **kwargs)


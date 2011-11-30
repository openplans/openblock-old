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
from ebdata.retrieval.scrapers.list_detail import ListDetailScraper
from ebdata.retrieval.utils import locations_are_close
from ebpub.db.models import Schema, NewsItem, Lookup, DataUpdate, field_mapping
from ebpub.geocoder import SmartGeocoder, GeocodingException, ParsingError, AmbiguousResult
from ebpub.geocoder.reverse import reverse_geocode

import datetime
import pytz

local_tz = pytz.timezone(settings.TIME_ZONE)

class NewsItemListDetailScraper(ListDetailScraper):
    """
    A ListDetailScraper that saves its data into the NewsItem table.

    Subclasses are required to set the `schema_slugs` attribute.

    Once you've set schema_slugs, there are a number of properties for
    conveniently accessing the relevant Schemas and SchemaFields:

    self.schemas lazily loads the list of Schema objects the first time it's
    accessed. It is a dictionary in the format {slug: Schema}.

    self.schema is available if schema_slugs has only one element. It's the
    Schema object.

    self.lookups lazily loads a dictionary of all SchemaFields with
    lookup=True. The dictionary is in the format {name: schemafield}.
    If schema_slugs has more than one element, self.lookups is a
    dictionary in the format {schema_slug: {name: schemafield}}.

    self.schema_fields lazily loads a dictionary of each SchemaField,
    mapping the name to the SchemaField object.
    If schema_slugs has more than one element, self.schema_fields is a
    dictionary in the format {schema_slug: {name: schema_field}}.

    self.schema_field_mapping lazily loads a dictionary of each
    SchemaField, mapping the name to the real_name.
    If schema_slugs has more than one element, self.schema_field_mapping
    is a dictionary in the format {schema_slug: {name: real_name}}.
    """
    schema_slugs = None
    logname = None

    def __init__(self, *args, **kwargs):
        if self.logname is None:
            self.logname = '%s.%s' % (settings.SHORT_NAME, self.schema_slugs[0])
        super(NewsItemListDetailScraper, self).__init__(*args, **kwargs)
        self._schema_cache = None
        self._schemas_cache = None
        self._lookups_cache = None
        self._schema_fields_cache = None
        self._schema_field_mapping_cache = None

    # schemas, schema, lookups and schema_field_mapping are all lazily loaded
    # so that this scraper can be run (in raw_data(), xml_data() or
    # display_data()) without requiring a valid database to be set up.

    @property
    def schemas(self):
        if self._schemas_cache is None:
            self._schemas_cache = dict([(s, Schema.objects.get(slug=s)) for s in self.schema_slugs])
        return self._schemas_cache

    @property
    def schema(self):
        if self._schema_cache is None:
            if len(self.schema_slugs) > 1:
                raise AttributeError('self.schema is only available if len(schema_slugs) == 1')
            self._schema_cache = self.schemas[self.schema_slugs[0]]
        return self._schema_cache

    @property
    def lookups(self):
        if self._lookups_cache is None:
            lc = dict([(s.slug, dict([(sf.name, sf) for sf in s.schemafield_set.filter(is_lookup=True)])) for s in self.schemas.values()])
            if len(self.schema_slugs) == 1:
                lc = lc[self.schema_slugs[0]]
            self._lookups_cache = lc
        return self._lookups_cache

    @property
    def schema_fields(self):
        if self._schema_fields_cache is None:
            sfs = dict([(s.slug, dict([(sf.name, sf)
                                       for sf in s.schemafield_set.all()]))
                        for s in self.schemas.values()])
            if len(self.schema_slugs) == 1:
                sfs = sfs[self.schema_slugs[0]]
            self._schema_fields_cache = sfs
        return self._schema_fields_cache

    @property
    def schema_field_mapping(self):
        if self._schema_field_mapping_cache is None:
            schema_objs = self.schemas.values()
            mapping = field_mapping([s.id for s in schema_objs])
            fm = dict([(s.slug, mapping[s.id]) for s in schema_objs])
            if len(self.schema_slugs) == 1:
                fm = fm[self.schema_slugs[0]]
            self._schema_field_mapping_cache = fm
        return self._schema_field_mapping_cache


    def get_or_create_lookup(self, schema_field_name, name, code, description='', schema=None, make_text_slug=True):
        """
        Returns the Lookup instance matching the given Schema slug, SchemaField
        name and Lookup.code, creating it (with the given name/code/description)
        if it doesn't already exist.

        If make_text_slug is True, then a slug will be created from the given
        name. If it's False, then the slug will be the Lookup's ID.
        """
        if len(self.schema_slugs) > 1:
            sf = self.lookups[schema][schema_field_name]
        else:
            sf = self.lookups[schema_field_name]
        return Lookup.objects.get_or_create_lookup(sf, name, code, description, make_text_slug, self.logger)



    def update(self):
        """
        Updates the Schema.last_updated fields after scraping is done.
        """
        self.num_added = 0
        self.num_changed = 0
        update_start = datetime.datetime.now()

        # We use a try/finally here so that the DataUpdate object is created
        # regardless of whether the scraper raised an exception.
        try:
            got_error = True
            super(NewsItemListDetailScraper, self).update()
            got_error = False
        finally:
            # Rollback, in case the database is in an aborted
            # transaction. This avoids the "psycopg2.ProgrammingError:
            # current transaction is aborted, commands ignored until
            # end of transaction block" error.
            from django.db import connection
            connection._rollback()

            update_finish = datetime.datetime.now()

            # Clear the Schema cache, in case the schemas have been
            # updated in the database since we started the scrape.
            self._schemas_cache = self._schema_cache = None

            for s in self.schemas.values():
                s.last_updated = datetime.date.today()
                s.save()
                DataUpdate.objects.create(
                    schema=s,
                    update_start=update_start,
                    update_finish=update_finish,
                    num_added=self.num_added,
                    num_changed=self.num_changed,
                    # None of our scrapers delete records yet, but we have the
                    # plumbing in place here in case future scrapers need to do
                    # that.
                    num_deleted=0,
                    num_skipped=self.num_skipped,
                    got_error=got_error,
                )


    def safe_location(self, location_name, geom, max_distance=200):
        """
        Returns a location (geometry) to use, given a location_name and
        geometry. This is used for data sources that publish both a geometry
        and a location_name -- we double-check that the geometry is within
        a certain `max_distance` from the geocoded location_name.

        If there's a discrepancy or if the location_name can't be geocoded,
        this returns None.
        """
        location = self.geocode(location_name)
        if location is None:
            return None
        location_point = location['point']
        if not location_point:
            return None
        location_point.srid = 4326
        is_close, distance = locations_are_close(location_point, geom, max_distance)
        if not is_close:
            return None
        return geom

    def last_updated_time(self, schema=None):
        """
        Returns a DateTime representing the last time we started
        scraping our schema(s).  (We use start time rather than end
        time on the assumption that a few overlaps are preferable to
        missing updates.)
        """
        schema = schema or self.schema
        try:
            last_update = DataUpdate.objects.order_by('update_start')[0]
            return last_update.update_start
        except IndexError:
            # Use the unix epoch (1970) as a stand-in for "never updated".
            return datetime.datetime.fromtimestamp(0)



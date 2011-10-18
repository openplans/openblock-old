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

from django.contrib.gis.db import models
from django.contrib.gis.db.models import Count
from django.core import urlresolvers
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from ebpub.geocoder.parser.parsing import normalize
from ebpub.streets.models import Block
from ebpub.utils.geodjango import flatten_geomcollection
from ebpub.utils.geodjango import ensure_valid
from ebpub.utils.text import slugify

import datetime
import logging
import re

logger = logging.getLogger('ebpub.db.models')

# Need these monkeypatches for "natural key" support during fixture load/dump.
import ebpub.monkeypatches
ebpub.monkeypatches.patch_once()

FREQUENCY_CHOICES = ('Hourly', 'Throughout the day', 'Daily', 'Twice a week', 'Weekly', 'Twice a month', 'Monthly', 'Quarterly', 'Sporadically', 'No longer updated')
FREQUENCY_CHOICES = [(a, a) for a in FREQUENCY_CHOICES]

logger = logging.getLogger('ebpub.db.models')

def get_valid_real_names():
    """
    Field names of ``Attribute``, suitable for use as
    ``SchemaField.real_name``.
    """
    for name in sorted(Attribute._meta.get_all_field_names()):
        if re.search(r'\d\d$', name):
            yield name


def field_mapping(schema_id_list):
    """
    Given a list of schema IDs, returns a dictionary of dictionaries, mapping
    schema_ids to dictionaries mapping the fields' name->real_name.
    Example return value:
        {1: {u'crime_type': 'varchar01', u'crime_date', 'date01'},
         2: {u'permit_number': 'varchar01', 'to_date': 'date01'},
        }
    """
    result = {}
    for sf in SchemaField.objects.filter(schema__id__in=(schema_id_list)).values('schema', 'name', 'real_name'):
        result.setdefault(sf['schema'], {})[sf['name']] = sf['real_name']
    return result


class SchemaManager(models.Manager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def get_query_set(self):
        """Warning: This breaks manage.py dumpdata.
        See bug #82.

        """
        return super(SchemaManager, self).get_query_set().defer(
            'short_description',
            'summary',
            'source',
            'grab_bag_headline',
            'grab_bag',
            'short_source',
            'update_frequency',
            'intro',
            )


class SchemaPublicManager(SchemaManager):

    def get_query_set(self):
        return super(SchemaManager, self).get_query_set().filter(is_public=True)

class Schema(models.Model):
    """
    Describes a type of NewsItem.  A NewsItem has exactly one Schema,
    which describes its Attributes, via associated SchemaFields.

    nb. to get all NewsItem instances for a Schema, you can do the usual as per
    http://docs.djangoproject.com/en/dev/topics/db/queries/#backwards-related-objects:
    schema.newsitem_set.all()
    """
    name = models.CharField(max_length=32)
    plural_name = models.CharField(max_length=32)
    indefinite_article = models.CharField(max_length=2,
                                          help_text="eg.'a' or 'an'")
    slug = models.SlugField(max_length=32, unique=True)
    min_date = models.DateField(
        help_text="The earliest available pub_date for this Schema")
    last_updated = models.DateField()
    date_name = models.CharField(
        max_length=32, default='Date',
        help_text='Human-readable name for the item_date field')
    date_name_plural = models.CharField(max_length=32, default='Dates')
    importance = models.SmallIntegerField(
        default=0,
        help_text='Bigger number is more important; used for sorting in some places.')
    is_public = models.BooleanField(
        db_index=True, default=False,
        help_text="Set False if you want only people with the staff cookie to be able to see it.") 
    is_special_report = models.BooleanField(
        default=False,
        help_text="Whether to use the schema_detail_special_report view for these items, eg. for displaying items that have a known general Location but not a specific point.")

    is_event = models.BooleanField(
        default=False,
        help_text="Whether these items are (potentially) future events rather than news in the past.")

    can_collapse = models.BooleanField(
        default=False,
        help_text="Whether RSS feed should collapse many of these into one.")

    has_newsitem_detail = models.BooleanField(
        default=False,
        help_text="Whether to show a detail page for NewsItems of this schema, or redirect to the NewsItem's source URL instead.")

    allow_comments = models.BooleanField(
        default=False,
        help_text="Whether to allow users to add comments to NewsItems of the schema. Only applies to items with detail page."
    )

    allow_charting = models.BooleanField(
        default=False,
        help_text="Whether aggregate charts are displayed on the home page of this Schema")

    uses_attributes_in_list = models.BooleanField(
        default=False,
        help_text="Whether attributes should be preloaded for NewsItems of this Schema, in the list view")


    number_in_overview = models.SmallIntegerField(
        default=5,
        help_text="Number of records to show on place_overview")

    map_icon_url = models.TextField(
        blank=True, null=True,
        help_text="Set this to a URL to a small image icon and it will be displayed on maps.")
    map_color = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="CSS Color used on maps to display this type of news. eg #FF0000.  Only used if map_icon_url is not set.")

    objects = SchemaManager()
    public_objects = SchemaPublicManager()

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)

    def url(self):
        return urlresolvers.reverse('ebpub-schema-detail', args=(self.slug,))

    ######################################################################
    # Metadata fields that used to live in a separate SchemaInfo model.
    short_description = models.TextField(blank=True, default='')
    summary = models.TextField(blank=True, default='')
    source = models.TextField(blank=True, default='',
                              help_text='Where this information came from, as one or more URLs, one per line.')
    grab_bag_headline = models.CharField(max_length=128, blank=True, default='') # Remove? #232
    grab_bag = models.TextField(blank=True, default='')  # Remove? #232
    short_source = models.CharField(max_length=128, blank=True, default='One-line description of where this information came from.')
    update_frequency = models.CharField(max_length=64, blank=True, default='',
                                        choices=FREQUENCY_CHOICES)
    intro = models.TextField(blank=True, default='')  # Remove? #232

    class Meta:
        ordering = ('name',)

class SchemaFieldManager(models.Manager):

    def get_by_natural_key(self, schema_slug, real_name):
        return self.get(schema__slug=schema_slug, real_name=real_name)

class SchemaField(models.Model):
    """
    Describes the meaning of one Attribute field for one Schema type.
    """
    objects = SchemaFieldManager()

    schema = models.ForeignKey(Schema)

    pretty_name = models.CharField(
        max_length=32,
        help_text="Human-readable name of this field, for display."
        )
    pretty_name_plural = models.CharField(
        max_length=32,
        help_text="Plural human-readable name"
        )

    name = models.SlugField(max_length=32)

    real_name = models.CharField(
        max_length=10,
        help_text="Column name in the Attribute model. 'varchar01', 'varchar02', etc.",
        choices=((name, name) for name in get_valid_real_names()),
        )
    display = models.BooleanField(
        default=True,
        help_text='Whether to display value on the public site.'
        )
    is_lookup = models.BooleanField(
        default=False,
        help_text='Whether the value is a foreign key to Lookup.'
        )
    is_filter = models.BooleanField(
        default=False,
        help_text='Whether to link to list of items with the same value in this field. Assumes is_lookup=True.'
        )
    is_charted = models.BooleanField(
        default=False,
        help_text='Whether the schema detail view displays a chart for this field; also see "trends" tabs on place overview page.'
        )
    display_order = models.SmallIntegerField(default=10)
    is_searchable = models.BooleanField(
        default=False,
        help_text="Whether the value is searchable by content. Doesn't make sense if is_lookup=True."
        )

    def natural_key(self):
        return (self.schema.slug, self.real_name)

    class Meta(object):
        unique_together = (('schema', 'real_name'),)
        ordering = ('pretty_name',)

    def __unicode__(self):
        return u'%s - %s' % (self.schema, self.name)

    @property
    def datatype(self):
        return self.real_name[:-2]

    def is_type(self, *data_types):
        """
        Returns True if this SchemaField is of *any* of the given data types.

        Allowed values are 'varchar', 'date', 'time', 'datetime', 'bool', 'int'.
        """
        return self.datatype in data_types

    def is_many_to_many_lookup(self):
        """
        Returns True if this SchemaField is a many-to-many lookup.
        """
        return self.is_lookup and not self.is_type('int')
    is_many_to_many_lookup.boolean = True

    def all_lookups(self):
        if not self.is_lookup:
            raise ValueError('SchemaField.all_lookups() can only be called if is_lookup is True')
        return Lookup.objects.filter(schema_field__id=self.id).order_by('name')

    def browse_by_title(self):
        "Returns FOO in 'Browse by FOO', for this SchemaField."
        if self.is_type('bool'):
            return u'whether they %s' % self.pretty_name_plural
        return self.pretty_name

    def smart_pretty_name(self):
        """
        Returns the pretty name for this SchemaField, taking into account
        many-to-many fields.
        """
        if self.is_many_to_many_lookup():
            return self.pretty_name_plural
        return self.pretty_name


class LocationTypeManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

class LocationType(models.Model):
    name = models.CharField(max_length=255,
                            help_text='for example, "Ward" or "Congressional District"')
    plural_name = models.CharField(max_length=64)
    scope = models.CharField(max_length=64,
                             help_text='e.g., "Chicago" or "U.S.A."')
    slug = models.SlugField(max_length=32, unique=True)
    is_browsable = models.BooleanField(
        default=True, help_text="Whether this is displayed on location_type_list.") #  XXX unused??
    is_significant = models.BooleanField(
        default=True,
        help_text="Whether this can be used to filter NewsItems, shows up in 'nearby locations', etc."
        )

    def __unicode__(self):
        return u'%s, %s' % (self.name, self.scope)

    def url(self):
        return urlresolvers.reverse('ebpub-loc-type-detail', args=(self.slug,))

    def natural_key(self):
        return (self.slug,)

    class Meta:
        ordering = ('name',)

    objects = LocationTypeManager()


class LocationManager(models.GeoManager):
    def get_by_natural_key(self, slug, location_type_slug):
        return self.get(slug=slug, location_type__slug=location_type_slug)

class Location(models.Model):
    name = models.CharField(max_length=255) # e.g., "35th Ward"
    normalized_name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=32, db_index=True)
    location_type = models.ForeignKey(LocationType)
    location = models.GeometryField(null=True)
    display_order = models.SmallIntegerField()
    city = models.CharField(max_length=255)
    source = models.CharField(max_length=64)
    area = models.FloatField(
        blank=True, null=True,
        help_text="In square meters. This is populated automatically."
        # the db trigger is created by ebpub/db/migrations/0004_st_intersects_patch.py.
        )
    population = models.IntegerField(blank=True, null=True) # from the 2000 Census
    user_id = models.IntegerField(
        blank=True, null=True,
        help_text="Used for 'custom' Locations created by end users.")
    is_public = models.BooleanField(
        help_text='Whether this is publically visible, or requires the staff cookie')
    description = models.TextField(blank=True)
    creation_date = models.DateTimeField(blank=True, null=True)
    last_mod_date = models.DateTimeField(blank=True, null=True)
    objects = LocationManager()

    @property
    def centroid(self):
        # For backward compatibility.
        import warnings
        warnings.warn(
            "Location.centroid is deprecated. Use Location.location.centroid instead.",
            DeprecationWarning)
        return self.location.centroid

    def clean(self):
        if self.location:
            try:
                self.location = ensure_valid(flatten_geomcollection(self.location))
            except ValueError, e:
                raise ValidationError(str(e))
        if self.normalized_name:
            self.normalized_name = normalize(self.normalized_name)
        else:
            self.normalized_name = normalize(self.name)

    class Meta:
        unique_together = (('slug', 'location_type'),)
        ordering = ('slug',)

    def natural_key(self):
        return (self.slug, self.location_type.slug)

    def __unicode__(self):
        return self.name

    def url(self):
        return urlresolvers.reverse('ebpub-location-recent',
                                    args=(self.location_type.slug, self.slug))

    def rss_url(self):
        return urlresolvers.reverse('ebpub-location-rss',
                                    args=(self.location_type.slug, self.slug))


    def alert_url(self):
        return urlresolvers.reverse('ebpub-location-alerts',
                                    args=(self.location_type.slug, self.slug))

    # Give Location objects a "pretty_name" attribute for interoperability with
    # Block objects. (Parts of our app accept either a Block or Location.)
    @property
    def pretty_name(self):
        return self.name

    @property
    def is_custom(self):
        return self.location_type.slug == 'custom'


class LocationSynonymManager(models.Manager):
    def get_canonical(self, name):
        """
        Returns the canonical normalized spelling of the given location name. 
        If the given location name is already correctly spelled, then it's returned as-is.
        """
        try:
            normalized_name = normalize(name)
            return self.get(normalized_name=normalized_name).location.normalized_name
        except self.model.DoesNotExist:
            return normalized_name

class LocationSynonym(models.Model):
    """
    represents a synonym for a Location
    """
    pretty_name = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255, db_index=True)
    location = models.ForeignKey(Location,
                                 help_text='Location this is a synonym for.')
    objects = LocationSynonymManager()

    def save(self):
        # Not doing this in clean() because we really don't want there to be
        # any way to get this wrong.
        if self.normalized_name:
            self.normalized_name = normalize(self.normalized_name)
        else:
            self.normalized_name = normalize(self.pretty_name)
        super(LocationSynonym, self).save()

    def __unicode__(self):
        return self.pretty_name

class AttributesDescriptor(object):
    """
    This class provides the functionality that makes the attributes available
    as `attributes` on a model instance.
    """
    def __get__(self, instance, instance_type=None):
        if instance is None:
            raise AttributeError("%s must be accessed via instance" % self.__class__.__name__)
        if not hasattr(instance, '_attributes_cache'):
            select_dict = field_mapping([instance.schema_id]).get(instance.schema_id, {})
            instance._attributes_cache = AttributeDict(instance.id, instance.schema_id, select_dict)
        return instance._attributes_cache

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("%s must be accessed via instance" % self.__class__.__name__)
        if not isinstance(value, dict):
            raise ValueError('Only a dictionary is allowed')
        mapping = field_mapping([instance.schema_id]).get(instance.schema_id, {}).items()
        if not mapping:
            if value:
                logger.warn("Can't save non-empty attributes dict with an empty schema")
            return
        values = [value.get(k, None) for k, v in mapping]
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE %s
            SET %s
            WHERE news_item_id = %%s
            """ % (Attribute._meta.db_table, ','.join(['%s=%%s' % v for k, v in mapping])),
                values + [instance.id])
        # If no records were updated, that means the DB doesn't yet have a
        # row in the attributes table for this news item. Do an INSERT.
        if cursor.rowcount < 1:
            cursor.execute("""
                INSERT INTO %s (news_item_id, schema_id, %s)
                VALUES (%%s, %%s, %s)""" % (Attribute._meta.db_table, ','.join([v for k, v in mapping]), ','.join(['%s' for k in mapping])),
                [instance.id, instance.schema_id] + values)
        transaction.commit_unless_managed()

class AttributeDict(dict):
    """
    A dictionary-like object that serves as a wrapper around attributes for a
    given NewsItem.
    """
    def __init__(self, news_item_id, schema_id, mapping):
        dict.__init__(self)
        self.news_item_id = news_item_id
        self.schema_id = schema_id
        self.mapping = mapping # name -> real_name dictionary
        self.cached = False

    def __do_query(self):
        if not self.cached:
            attr_values = Attribute.objects.filter(news_item__id=self.news_item_id).extra(select=self.mapping).values(*self.mapping.keys())
            # Rarely, we might have added the first SchemaField for this
            # Schema *after* the NewsItem was scraped.  In that case
            # attr_values will be empty list.
            if attr_values:
                self.update(attr_values[0])
            self.cached = True

    def __len__(self):
        # So len(self) and bool(self) work.
        self.__do_query()
        return dict.__len__(self)

    def keys(self, *args, **kwargs):
        self.__do_query()        
        return dict.keys(self, *args, **kwargs)

    def items(self, *args, **kwargs):
        self.__do_query()        
        return dict.items(self, *args, **kwargs)

    def get(self, *args, **kwargs):
        self.__do_query()
        return dict.get(self, *args, **kwargs)

    def __getitem__(self, name):
        self.__do_query()
        return dict.__getitem__(self, name)

    def __setitem__(self, name, value):
        # TODO: refactor, code overlaps largely with AttributeDescriptor.__set__
        cursor = connection.cursor()
        real_name = self.mapping[name]
        cursor.execute("""
            UPDATE %s
            SET %s = %%s
            WHERE news_item_id = %%s
            """ % (Attribute._meta.db_table, real_name), [value, self.news_item_id])
        # If no records were updated, that means the DB doesn't yet have a
        # row in the attributes table for this news item. Do an INSERT.
        if cursor.rowcount < 1:
            cursor.execute("""
                INSERT INTO %s (news_item_id, schema_id, %s)
                VALUES (%%s, %%s, %%s)""" % (Attribute._meta.db_table, real_name),
                [self.news_item_id, self.schema_id, value])
        transaction.commit_unless_managed()
        dict.__setitem__(self, name, value)

class NewsItemQuerySet(models.query.GeoQuerySet):

    def prepare_attribute_qs(self):
        clone = self._clone()
        if 'db_attribute' not in clone.query.extra_tables:
            clone = clone.extra(tables=('db_attribute',))
        # extra_where went away in Django 1.1.
        # This seems to be the correct replacement as per
        # http://docs.djangoproject.com/en/dev/ref/models/querysets/
        clone = clone.extra(where=('db_newsitem.id = db_attribute.news_item_id',))
        return clone

    def by_attribute(self, schema_field, att_value, is_lookup=False):
        """
        Returns a QuerySet of NewsItems whose attribute value for the given
        SchemaField is att_value. If att_value is a list, this will do the
        equivalent of an "OR" search, returning all NewsItems that have an
        attribute value in the att_value list.

        This handles many-to-many lookups correctly behind the scenes.

        If is_lookup is True, then att_value is treated as the 'code' of a
        Lookup object, and the Lookup's ID will be retrieved for use in the
        query.
        """

        clone = self.prepare_attribute_qs()
        real_name = str(schema_field.real_name)
        if not isinstance(att_value, (list, tuple)):
            att_value = [att_value]
        if is_lookup:
            if not isinstance(att_value[0], Lookup):
                # Assume all are Lookup.code values.
                att_value = Lookup.objects.filter(schema_field__id=schema_field.id, code__in=att_value)
            if not att_value:
                # If the lookup values don't exist, then there aren't any
                # NewsItems with this attribute value. Note that we aren't
                # using QuerySet.none() here, because we want the result to
                # be a NewsItemQuerySet, and none() returns a normal QuerySet.
                clone = clone.extra(where=('1=0',))
                return clone
            att_value = [val.id for val in att_value]
        if schema_field.is_many_to_many_lookup():
            # We have to use a regular expression search to look for all rows
            # with the given att_value *somewhere* in the column. The [[:<:]]
            # thing is a word boundary.
            for value in att_value:
                if not str(value).isdigit():
                    raise ValueError('Only integer strings allowed for att_value in many-to-many SchemaFields')
            clone = clone.extra(where=("db_attribute.%s ~ '[[:<:]]%s[[:>:]]'" % (real_name, '|'.join([str(val) for val in att_value])),))
        elif None in att_value:
            if att_value != [None]:
                raise ValueError('by_attribute() att_value list cannot have more than one element if it includes None')
            clone = clone.extra(where=("db_attribute.%s IS NULL" % real_name,))
        else:
            clone = clone.extra(where=("db_attribute.%s IN (%s)" % (real_name, ','.join(['%s' for val in att_value])),),
                                params=tuple(att_value))
        return clone

    def date_counts(self):
        """
        Returns a dictionary mapping {item_date: count}.
        """
        from django.db.models.query import QuerySet
        qs = QuerySet.values(self, 'item_date').annotate(count=models.Count('id'))
        # Turn off ordering, as that breaks Count; see https://docs.djangoproject.com/en/dev/topics/db/aggregation/#interaction-with-default-ordering-or-order-by
        qs = qs.order_by()
        return dict([(v['item_date'], v['count']) for v in qs])

    def top_lookups(self, schema_field, count):
        """
        Returns a list of {lookup, count} dictionaries representing the top
        Lookups for this QuerySet.
        """
        real_name = "db_attribute." + str(schema_field.real_name)
        if schema_field.is_many_to_many_lookup():
            # First prepare a subquery to get a *single* count of
            # attribute rows that match each relevant m2m lookup
            # value.  It's very important to get a single row here or
            # else we get a DataBaseError with "more than one row
            # returned by a subquery used as an expression". (Bug #146)
            clone = self.prepare_attribute_qs()
            clone = clone.filter(schema__id=schema_field.schema_id)
            # This is a regex search for the lookup id.
            clone = clone.extra(where=[real_name + " ~ ('[[:<:]]' || db_lookup.id || '[[:>:]]')"])
            # We want to count the current queryset and get a single
            # row for injecting into the subsequent Lookup query, but
            # we don't want Django's aggregation support to
            # automatically group by fields that aren't relevant and
            # would cause multiple rows as a result. So we call
            # `values()' on a field that we're already filtering by,
            # in this case, schema, as essentially a harmless identify
            # function.
            # See http://docs.djangoproject.com/en/dev/topics/db/aggregation/#values
            clone = clone.values('schema')

            # Fix #146: Having any `ORDER BY foo` in this subquery causes
            # Django to also add a `GROUP BY foo`, which potentially
            # returns multiple rows. So, remove the ordering.
            clone = clone.order_by()
            clone = clone.annotate(count=Count('schema'))
            # Unusual: We don't run the clone query, we just stuff its SQL
            # into our Lookup qs.
            qs = Lookup.objects.filter(schema_field__id=schema_field.id)
            qs = qs.extra(select={'lookup_id': 'id', 'item_count': clone.values('count').query})
        else:
            # Counts of attribute rows matching each relevant Lookup.
            # Much easier when is_many_to_many_lookup == False :-)
            qs = self.prepare_attribute_qs().extra(select={'lookup_id': real_name})
            qs.query.group_by = [real_name]
            qs = qs.values('lookup_id').annotate(item_count=Count('id'))

        qs = qs.values('lookup_id', 'item_count').order_by('-item_count')
        ids_and_counts = [(v['lookup_id'], v['item_count']) for v in qs
                          if v['item_count']]
        ids_and_counts = ids_and_counts[:count]
        lookup_objs = Lookup.objects.in_bulk([i[0] for i in ids_and_counts])
        return [{'lookup': lookup_objs[i[0]], 'count': i[1]} for i in ids_and_counts
                if not None in i]

    def text_search(self, schema_field, query):
        """
        Returns a QuerySet of NewsItems whose attribute for
        a given schema field matches a text search query.
        """
        clone = self.prepare_attribute_qs()
        query = query.lower()

        clone = clone.extra(where=("db_attribute." + str(schema_field.real_name) + " ILIKE %s",),
                            params=("%%%s%%" % query,))
        return clone

class NewsItemManager(models.GeoManager):
    def get_query_set(self):
        return NewsItemQuerySet(self.model)

    def by_attribute(self, *args, **kwargs):
        return self.get_query_set().by_attribute(*args, **kwargs)

    def text_search(self, *args, **kwargs):
        return self.get_query_set().text_search(*args, **kwargs)

    def date_counts(self, *args, **kwargs):
        return self.get_query_set().date_counts(*args, **kwargs)

    def top_lookups(self, *args, **kwargs):
        return self.get_query_set().top_lookups(*args, **kwargs)

class NewsItem(models.Model):
    """
    Lowest common denominator metadata for News-like things.

    self.schema and self.attributes are used for extended metadata;
    If all you want is to examine the attributes, self.attributes
    can be treated like a dict.
    (Internally it's a bit complicated. See the Schema, SchemaField, and
    Attribute models, plus AttributeDescriptor, for how it all works.)

    NewsItems have several distinct notions of location:

    * self.location_name is a human-readable version of the location;
      it can be anything, but typically it describes an address,
      block, geographic area, or landmark.

    * The NewsItemLocation model is for fast lookups of NewsItems to
      all Locations where the .location fields overlap.  This is set
      by a sql trigger whenever self.location changes; not set by any
      python code. Used in various views for filtering.

    * self.location is typically a point, and is used in views for
      filtering newsitems. Theoretically (untested!!) could also be a
      GeometryCollection, for news items that mention multiple
      places. This is typically set during scraping, by geocoding if
      not provided in the source data.

    * self.location_object is a Location and a) is usually Null in
      practice, and b) is only needed by self.location_url(), so we
      can link back to a location view from a newsitem view.  It would
      be set during scraping.  (Example use case: NYC crime
      aggregates, where there's no location or address data for the
      "news item" other than which precinct it occurs in.
      eg. http://nyc.everyblock.com/crime/by-date/2010/8/23/3364632/ )

    * self.block is optionally one Block. Also set during
      scraping/geocoding.  So far can't find anything that actually
      uses these.
    """

    # We don't have a natural_key() method because we don't know for
    # sure that anything other than ID will be unique.

    schema = models.ForeignKey(Schema)
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.TextField(
        blank=True,
        help_text="link to original source for this news")
    pub_date = models.DateTimeField(
        db_index=True,
        help_text='Date/time this Item was added to the OpenBlock site.')  # TODO: default to now()
    item_date = models.DateField(
        db_index=True,
        help_text='Date (no time) this Item occurred, or was published on the original source site.')  # TODO: default to now()

    # automatic last modification tracking.  Note: if changing only attributes, the the
    # NewsItem should also be save()'d to update last_modification when complete. 
    last_modification = models.DateTimeField(db_index=True, auto_now=True)
    
    location = models.GeometryField(blank=True, null=True, spatial_index=True,
                                    help_text="Coordinates where this news occurred.")
    location_name = models.CharField(max_length=255,
                                     help_text="Human-readable address or name of place where this news item occurred.")
    location_object = models.ForeignKey(Location, blank=True, null=True,
                                        help_text="Optional reference to a Location where this item occurred, for use when we know the general area but not specific coordinates.")
    block = models.ForeignKey(Block, blank=True, null=True,
                              help_text="Optional reference to a Block. Not really used")

    objects = NewsItemManager()
    attributes = AttributesDescriptor()  # Treat it like a dict.


    def clean(self):
        self.location = ensure_valid(flatten_geomcollection(self.location))

    class Meta:
        ordering = ('title',)

    def __unicode__(self):
        return self.title or 'Untitled News Item'

    def item_url(self):
        return urlresolvers.reverse('ebpub-newsitem-detail',
                                    args=[self.schema.slug, self.id], kwargs={})

    def item_url_with_domain(self):
        from django.conf import settings
        return 'http://%s%s' % (settings.EB_DOMAIN, self.item_url())

    def item_date_url(self):
        from ebpub.db.schemafilters import FilterChain
        chain = FilterChain(schema=self.schema)
        chain.add('date', self.item_date)
        return chain.make_url()

    def location_url(self):
        if self.location_object_id is not None:
            return self.location_object.url()
        return None

    def attributes_for_template(self):
        """
        Return a list of AttributeForTemplate objects for this NewsItem. The
        objects are ordered by SchemaField.display_order.
        """
        fields = SchemaField.objects.filter(schema__id=self.schema_id).select_related().order_by('display_order')
        if not fields:
            return []
        if not self.attributes:
            logger.warn("%s has fields in its schema, but no attributes!" % self)
            return []
        return [AttributeForTemplate(f, self.attributes) for f in fields]


class AttributeForTemplate(object):
    def __init__(self, schema_field, attribute_row):
        self.sf = schema_field
        self.raw_value = attribute_row[schema_field.name]
        self.schema_slug = schema_field.schema.slug
        self.is_lookup = schema_field.is_lookup
        self.is_filter = schema_field.is_filter
        if self.is_lookup:
            # Earlier queries may have already looked up Lookup instances.
            # Don't do unnecessary work.
            if isinstance(self.raw_value, Lookup):
                self.values = [self.raw_value]
            elif (isinstance(self.raw_value, list) and self.raw_value
                  and isinstance(self.raw_value[0], Lookup)):
                self.values = self.raw_values
            elif self.raw_value is None or self.raw_value == '':
                self.values = []
            elif self.sf.is_many_to_many_lookup():
                try:
                    id_values = map(int, self.raw_value.split(','))
                except ValueError:
                    self.values = []
                else:
                    lookups = Lookup.objects.in_bulk(id_values)
                    self.values = [lookups[i] for i in id_values]
            else:
                self.values = [Lookup.objects.get(id=self.raw_value)]
        else:
            self.values = [self.raw_value]

    def value_list(self):
        """
        Returns a list of {value, url, description} dictionaries
        representing each value for this attribute.
        """
        from django.utils.dateformat import format, time_format
        # Setting these to [None] ensures that zip() returns a list
        # of at least length one.
        urls = [None]
        descriptions = [None]
        if self.is_filter:
            from ebpub.db.schemafilters import FilterChain
            chain = FilterChain(schema=self.sf.schema)
            if self.is_lookup:
                urls = [chain.replace(self.sf, look).make_url() if look else None
                        for look in self.values]
            else:
                urls = [chain.replace(self.sf, self.raw_value).make_url()]
        if self.is_lookup:
            values = [val and val.name or 'None' for val in self.values]
            descriptions = [val and val.description or None for val in self.values]
        elif isinstance(self.raw_value, datetime.datetime):
            values = [format(self.raw_value, 'F j, Y, P')]
        elif isinstance(self.raw_value, datetime.date):
            values = [format(self.raw_value, 'F j, Y')]
        elif isinstance(self.raw_value, datetime.time):
            values = [time_format(self.raw_value, 'P')]
        elif self.raw_value is True:
            values = ['Yes']
        elif self.raw_value is False:
            values = ['No']
        elif self.raw_value is None:
            values = ['N/A']
        else:
            values = [self.raw_value]
        return [{'value': value, 'url': url, 'description': description} for value, url, description in zip(values, urls, descriptions)]

class Attribute(models.Model):
    """
    Extended metadata for NewsItems.

    Each row contains all the extra metadata for one NewsItem
    instance.  The field names are generic, so in order to know what
    they mean, you must look at the SchemaFields for the Schema for
    that NewsItem.  eg. newsitem.

    """
    news_item = models.OneToOneField(NewsItem, primary_key=True, unique=True)
    schema = models.ForeignKey(Schema)
    # All data-type field names must end in two digits, because the code assumes this.
    varchar01 = models.CharField(max_length=4096, blank=True, null=True)
    varchar02 = models.CharField(max_length=4096, blank=True, null=True)
    varchar03 = models.CharField(max_length=4096, blank=True, null=True)
    varchar04 = models.CharField(max_length=4096, blank=True, null=True)
    varchar05 = models.CharField(max_length=4096, blank=True, null=True)
    date01 = models.DateField(blank=True, null=True)
    date02 = models.DateField(blank=True, null=True)
    date03 = models.DateField(blank=True, null=True)
    date04 = models.DateField(blank=True, null=True)
    date05 = models.DateField(blank=True, null=True)
    time01 = models.TimeField(blank=True, null=True)
    time02 = models.TimeField(blank=True, null=True)
    datetime01 = models.DateTimeField(blank=True, null=True)
    datetime02 = models.DateTimeField(blank=True, null=True)
    datetime03 = models.DateTimeField(blank=True, null=True)
    datetime04 = models.DateTimeField(blank=True, null=True)
    bool01 = models.NullBooleanField(blank=True)
    bool02 = models.NullBooleanField(blank=True)
    bool03 = models.NullBooleanField(blank=True)
    bool04 = models.NullBooleanField(blank=True)
    bool05 = models.NullBooleanField(blank=True)
    int01 = models.IntegerField(blank=True, null=True)
    int02 = models.IntegerField(blank=True, null=True)
    int03 = models.IntegerField(blank=True, null=True)
    int04 = models.IntegerField(blank=True, null=True)
    int05 = models.IntegerField(blank=True, null=True)
    int06 = models.IntegerField(blank=True, null=True)
    int07 = models.IntegerField(blank=True, null=True)
    text01 = models.TextField(blank=True, null=True)
    text02 = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'Attributes for news item %s' % self.news_item_id

class LookupManager(models.Manager):

    def get_by_natural_key(self, slug, schema_field__slug,
                           schema_field__real_name):
        return self.get(slug=slug, schema_field__slug=schema_field__slug,
                        schema_field__real_name=schema_field__real_name)

    def get_or_create_lookup(self, schema_field, name, code=None, description='', make_text_slug=True, logger=None):
        """
        Returns the Lookup instance matching the given SchemaField, name and
        Lookup.code, creating it (with the given name/code/description) if it
        doesn't already exist.

        If make_text_slug is True, then a slug will be created from the given
        name. If it's False, then the slug will be the Lookup's ID.
        """
        def log_info(message):
            if logger is None:
                return
            logger.info(message)
        def log_warn(message):
            if logger is None:
                return
            logger.warn(message)
        code = code or name # code defaults to name if it wasn't provided
        try:
            obj = Lookup.objects.get(schema_field__id=schema_field.id, code=code)
        except Lookup.DoesNotExist:
            if make_text_slug:
                slug = slugify(name)
                if len(slug) > 32:
                    # Only bother to warn if we're actually going to use the slug.
                    if make_text_slug:
                        log_warn("Trimming slug %r to %r in order to fit 32-char limit." % (slug, slug[:32]))
                    slug = slug[:32]
            else:
                # To avoid integrity errors in the slug when creating the Lookup,
                # use a temporary dummy slug that's guaranteed not to be in use.
                # We'll change it back immediately afterward.
                slug = '__3029j3f029jf029jf029__'
            if len(name) > 255:
                old_name = name
                name = name[:250] + '...'
                # Save the full name in the description.
                if not description:
                    description = old_name
                log_warn("Trimming name %r to %r in order to fit 255-char limit." % (old_name, name))
            obj = Lookup(schema_field_id=schema_field.id, name=name, code=code, slug=slug, description=description)
            obj.save()
            if not make_text_slug:
                # Set the slug to the ID.
                obj.slug = obj.id
                obj.save()
            log_info('Created %s %r' % (schema_field.name, name))
        return obj

class Lookup(models.Model):
    schema_field = models.ForeignKey(SchemaField)
    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=255, blank=True,
        help_text='Optional internal code to use for retrieval if `name` is modified from the original data source, eg. to make `name` prettier.')
    # ... For example, in scraping Chicago crimes, we use the crime type code
    # to find the appropriate crime type in this table. We can't use `name`
    # in that case, because we've massaged `name` to use a "prettier"
    # formatting than exists in the data source.

    slug = models.SlugField(max_length=32, db_index=True)
    description = models.TextField(blank=True)

    objects = LookupManager()

    class Meta:
        unique_together = (('slug', 'schema_field'),
                           ('code', 'schema_field'),
                          )
        ordering = ('slug',)

    def natural_key(self):
        return (self.slug, self.schema_field.schema.slug,
                self.schema_field.real_name)

    def __unicode__(self):
        return u'%s - %s' % (self.schema_field, self.name)

class NewsItemLocation(models.Model):
    """
    Many-to-many mapping of NewsItems to Locations where the geometries intersect.
    Populated by triggers.
    """
    news_item = models.ForeignKey(NewsItem)
    location = models.ForeignKey(Location)

    class Meta:
        unique_together = (('news_item', 'location'),)

    def __unicode__(self):
        return u'%s - %s' % (self.news_item, self.location)


#############################################################################
# Aggregates.
# These provide for quick lookups of NewsItems by various buckets,
# eg. number of NewsItems added on one day.

class AggregateBaseClass(models.Model):
    schema = models.ForeignKey(Schema)
    total = models.IntegerField()

    class Meta:
        abstract = True

class AggregateAll(AggregateBaseClass):
    """Total items in the schema.
    """
    pass

class AggregateDay(AggregateBaseClass):
    """Total items in the schema with item_date on the given day
    """
    date_part = models.DateField(db_index=True)

class AggregateLocation(AggregateBaseClass):
    """Total items in the schema in location, summed over that last 30 days
    """
    location_type = models.ForeignKey(LocationType)
    location = models.ForeignKey(Location)

class AggregateLocationDay(AggregateBaseClass):
    """Total items in the schema in location with item_date on the given day
    """
    location_type = models.ForeignKey(LocationType)
    location = models.ForeignKey(Location)
    date_part = models.DateField(db_index=True)

class AggregateFieldLookup(AggregateBaseClass):
    """Total items in the schema with schema_field's value = lookup
    """
    schema_field = models.ForeignKey(SchemaField)
    lookup = models.ForeignKey(Lookup)

class SearchSpecialCase(models.Model):
    """
    Used as a fallback for location searches that don't match
    any Location, Intersection, etc.
    """
    query = models.CharField(
        max_length=64, unique=True,
        help_text='Normalized form of search queries that match this special case.'
        )  # TODO: normalize this on save
    redirect_to = models.CharField(
        max_length=255, blank=True,
        help_text='Optional absolute URL to redirect to on searches that match the query.')
    title = models.CharField(
        max_length=128, blank=True,
        help_text="Title to display on the results page if we don't redirect."
        )
    body = models.TextField(
        blank=True,
        help_text="Body to display on the result page if we don't redirect. HTML is OK.")

    def __unicode__(self):
        return self.query

class DataUpdate(models.Model):
    """Scraper scripts can use this to keep track of
    each time we populate NewsItems of a given Schema.
    """
    schema = models.ForeignKey(Schema)
    update_start = models.DateTimeField(
        help_text="When the scraper/importer started running.")
    update_finish = models.DateTimeField(
        help_text="When the scraper/importer finished.")
    num_added = models.IntegerField()
    num_changed = models.IntegerField()
    num_deleted = models.IntegerField()
    num_skipped = models.IntegerField()
    got_error = models.BooleanField()

    def __unicode__(self):
        return u'%s started on %s' % (self.schema.name, self.update_start)

    def total_time(self):
        return self.update_finish - self.update_start

def get_city_locations():
    """
    If we have configured multiple_cities, find all Locations
    of the city_location_type.
    Otherwise, empty query set.
    """
    from ebpub.metros.allmetros import get_metro
    metro = get_metro()
    if metro['multiple_cities']:
        cities = Location.objects.filter(location_type__slug=metro['city_location_type'])
        cities = cities.exclude(location_type__name__startswith='Unknown')
        return cities
    else:
        return Location.objects.filter(id=None)

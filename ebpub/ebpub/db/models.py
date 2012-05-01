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

"""

.. _newsitems:

.. _newsitem-schemas:

Overview: NewsItems and Schemas
===============================

The ebpub system is capable of handling
many disparate types of news -- e.g., crime, photos and restaurant inspections.
Each type of news is referred to as a :py:class:`Schema`,
and an individual piece of news is a :py:class:`NewsItem`.

.. _newsitem_core_fields:

Core Fields of NewsItems
------------------------

The :py:class:`NewsItem <NewsItem>` model in itself is generic -- a
lowest-common denominator of each piece of news on the site. It has:

* title (required)
* url (optional)
* description (optional)
* location_name (optional but highly desirable; can be reverse-geocoded from location if you have one)
* location (optional but highly desirable; can be geocoded from location_name if you have one)
* item_date (default: today)
* pub_date (default: current date and time)

.. _newsitem_attributes:

Flexible data: SchemaFields and Attributes
------------------------------------------

If you'd like to extend your NewsItems to include
more information, you can use :py:class:`SchemaFields <SchemaField>`.

Each piece of news is described by:

* One :py:class:`NewsItem` instance, with just the core fields like
  title and description.

* One corresponding :py:class:`Attribute` instance, which is a dictionary-like
  object containing extra data, and is available as ``newsitem.attributes``.

* One :py:class:`Schema` that identifies the "type" of NewsItem; and

* A set of :py:class:`SchemaFields <SchemaField>`, each of which describes:
  a valid key for the attributes dictionary; the type of its allowed values;
  and some configuration metadata about how to display and use that attribute.

This is intended to be flexible enough for real-world news data, while
still allowing for fast database queries.  For more background,
you might be interested in the video
`Behind the scenes of EveryBlock.com <http://blip.tv/file/1957362>`_.

.. admonition:: Why not NoSQL?

   ebpub was originally written around the time of the rise in popularity of
   schemaless document storage systems commonly lumped together as
   `nosql <http://en.wikipedia.org/wiki/Nosql>`_,
   which would have made this one aspect of ebpub rather trivial.
   However, at the time, none of them had much in the way of
   geospatial capabilities; even today, none of them are as
   full-featured as PostGIS.


Examples might make this clearer. To assign the whole ``attributes`` dictionary::

    ni = NewsItem.objects.get(...)
    ni.attributes = {'sale_price': 19}
    # There is no need to call ni.save() or ni.attributes.save();
    # the assignment operation does that behind the scenes.

To assign a single value::

    ni.attributes['sale_price'] = 19
    # Again there is no need to save() anything explicilty.

To get a value::

    print ni.attributes['sale_price']

Or, from a database perspective: The "db_attribute" table stores
arbitrary attributes for each NewsItem, and the "db_schemafield" table
is the key for those attributes.
A SchemaField says, for example, that
the "int01" column in the db_attribute table for the "real estate
sales" Schema corresponds to the "sale price".

We'll walk through this example in detail below.


Detailed Example
------------------

Imagine you have a "real estate sales"
Schema, with an id of 5. Say, for each sale, you want to store the following
information:

* address
* sale date
* sale price

The first two fields should go in ``NewsItem.location_name`` and ``NewsItem.item_date``,
respectively -- there's no reason to put them in the Attribute table, because
the NewsItem table has a slot for them.

Sale price is a number (we'll assume it's an integer), so create a
:py:class:`SchemaField` defining it, with these values:

.. code-block:: python
    :linenos:

    field = SchemaField(schema_id = 5,
        name = 'sale_price',
        real_name = 'int01',
        pretty_name = 'sale price',
        pretty_name_plural = 'sale prices',
        display = True,
        display_order = 1,
        is_searchable = False,
       )

Line 1. ``schema_id`` is the id of our "real estate sales" schema.

Line 2.      ``name`` is the alphanumeric-and-underscores-only name for this field.
(Used in URLs, and as the key for ``newsitem.attributes``,
and for the
:py:meth:`NewsItemQuerySet.by_attribute` method.)
This value must be unique with respect to the schema_id.

Line 3.  ``real_name`` is the column to use in the db_attribute model. Choices are:
int01-07, text01, bool01-05, datetime01-04, date01-05, time01-02,
varchar01-05. This value must be unique with respect to the schema_id.

Lines 4-5. ``pretty_name`` and ``pretty_name_plural`` are the human-readable name
for this attribute.

Line 6.  ``display`` controls whether to display the value on the site.

Line 7: `sort_order`` - An integer representing what order it should be displayed
on newsitem_detail pages.

Line 8: ``is_searchable`` - Whether you can do text searches on this field.
Only works with text or varchar fields.

Once you've created this SchemaField, the value of "int01" for any db_attribute
row with schema_id=5 will be the sale price.

Having done all that, using the field is as easy as::

   from ebpub.db.models import NewsItem
   ni = NewsItem(schema__id=5, title='the title', description='the description', ...)
   ni.save()
   ni.attributes['sale_price'] = 59


Searching by Attributes
------------------------

There is a simple API for searching NewsItems by attribute values:

   sale_price = SchemaField.objects.get(schema__id=5, name='sale_price')
   NewsItem.objects.filter(schema__id=5).by_attribute(sale_price, 59)

For details see :py:meth:`NewsItemQuerySet.by_attribute`.


Attributes: Under the hood
---------------------------

The dictionary-like API is provided thanks to the combination of
the ``AttributesDescriptor``, ``AttributeDict``, and
:py:class:`Attribute` classes; see the source code for details.

Images
------

NewsItems have a ``newsitemimage_set`` reverse relationship
with the :py:class:`NewsItemImage` model, allowing any number of
images to be associated with one NewsItem.
All the images for a NewsItem can be retrieved via
``item.newsitemimage_set.all()``.


Dates
-----

The distinction between ``NewsItem.pub_date`` and ``NewsItem.item_date``
is intended for data sets where there's
a lag in publishing or where the data is updated infrequently or
irregularly. 

For example, on EveryBlock.com, Chicago crime data is published a week
after it is reported, so a crime's ``item_date`` is the day of the
crime report, whereas the ``pub_date`` is the day the data was
published to EveryBlock.com.

Location, location, location
-----------------------------

NewsItems have several distinct notions of location:

* ``NewsItem.location_name`` is a human-readable version of the location;
  it can be anything, but typically it describes an address,
  block, geographic area, or landmark.

* ``NewsItem.location`` is used frequently; typically a point, and
  typically set when scraping data, by geocoding if
  not provided in the source data.  This is used in
  many views for finding relevant NewsItems (indirectly; actually
  see below about NewsItemLocations).

* ``NewsItem.location_set`` is a convenient way to get
  all :py:class:`Locations <Location>` that overlap this item's ``location``.
  It's a many-to-many relationship (via the
  NewsItemLocation model).  The NewsItemLocations are created by a sql trigger
  whenever self.location changes; not set by any python code. Used
  in various views for filtering.

* ``NewsItem.location_object`` is a single :py:class:`Location` reference;
  theoretically to be explicitly assigned by a scraper script when
  there's no known address or geographic point for this NewsItem
  but we know the name of the general area it's within.

  For example, many stories might mention a town or city name, or a
  police report might tell you the precinct.  In practice, this field
  is usually Null; more importantly it's only used currently
  (2011-12-06) by self.location_url(), for linking back to a location
  view from a newsitem view.  (Example of where everyblock.com uses
  this: NYC crime aggregates,
  eg. http://nyc.everyblock.com/crime/by-date/2010/8/23/3364632/ )

  See also this ticket http://developer.openblockproject.org/ticket/93
  about possibly making more use of self.location_object.


.. _aggregates:

Aggregates
----------

Several parts of ebpub display aggregate totals of NewsItems for a particular
Schema; for example, charts of how many were added each day.

Because these calculations can be expensive, there's an infrastructure
for caching the aggregate numbers regularly in separate tables (db_aggregate*).

To do this, just run the :py:mod:`update_aggregates <ebpub.db.bin.update_aggregates>`
script on the command line.

You'll want to do this on a regular basis, depending on how often you update
your data. **Some parts of the site (such as charts) will not be visible** until
you populate the aggregates.

.. _future_events:

Event-like News Types
----------------------

In order for OpenBlock to treat a news type as being about
(potentially) future events, rather than news from the (recent) past,
there is a simple convention that you should follow:

1. Set the schema's ``is_event=True``.

2. Add a SchemaField with ``name='start_time'``. It should be a Time
   field, i.e. ``real_name`` should be one of ``time01``, ``time02``,
   etc.  Leave ``is_filter``, ``is_lookoup``, ``is_searchable``, and
   ``is_charted`` set to False.  The ``pretty_name`` can be whatever
   you like of course.

3. Optionally add another SchemaField with ``name='end_time'``, if your data
   source will include this information.

4. When adding NewsItems of this type, the NewsItem's ``item_date``
   field should be set to the date on which the event will (or already
   did) take place, and ``attributes['start_time']`` should be set to
   the (local) time it will start, and ``attributes['end_time']``
   (if needed) should be set to the (local) end time.

All-day events can be represented by leaving ``start_time`` empty.

There is no special support for repeating events or other advanced
calendar features.

.. _lookups:

Lookups
========

Lookups are a way to reduce duplication and support fast searching
for similar NewsItems.

Consider the "real estate" schema we talked about in earlier examples.
We want to add a field representing "property type" for each real estate sale
NewsItem.

We could store it as a varchar field (in which case we'd set
real_name='varchar01') -- but that would cause a lot of duplication and
redundancy, because there are only a couple of property types -- the set
['single-family', 'condo', 'land', 'multi-family']. To represent this set,
we can use a Lookup -- a way to normalize the data.

To do this, set ``SchemaField.is_lookup=True`` and make sure to use an 'int' column
for SchemaField.real_name.  For example:

.. code-block:: python

    field = SchemaField(schema_id = 5,
        name = 'property_type',
        real_name = 'int02',
        is_lookup=True,
        pretty_name = 'property type',
        pretty_name_plural = 'property types',
        display = True,
        display_order = 2,
       )


Then, for each record, get or create a :py:class:`Lookup`
object that represents the data, and use
the Lookup's id in the appropriate attribute field.
For example:

.. code-block:: python

    condo = Lookup.objects.get_or_create_lookup(
        schema_field=field, name='condo')
    newsitem['property_type'] = condo

Note the convenience function :py:meth:`Lookup.objects.get_or_create_lookup() <LookupManager.get_or_create_lookup>`.

Many-to-many Lookups
--------------------

Sometimes a :py:class:`NewsItem` has multiple values for a single attribute.
For example, a restaurant inspection can have multiple violations. In
this case, you can use a many-to-many Lookup. To do this, just set
``SchemaField.is_lookup=True`` as before, but use a varchar field for
the ``SchemaField.real_name``. Then, in the db_attribute column, set
the value to a string of comma-separated integers of the Lookup IDs:

.. code-block:: python

    field = SchemaField.objects.get(schema_id=5, name='property_type')
    field.real_name = 'varchar01'
    field.save()

    newsitem.attributes['property_type'] = '1,2,3'


.. _featured_lookups:

"Featured" Lookups
-----------------------

A :py:class:`Lookup` instance can have ``featured=True``, which you can use to
mark some Lookup values as "special" for eg. navigation purposes.
One example use case would be special tags or keywords that mark
any relevant NewsItems for inclusion in a special part of your homepage.

To work with Lookups that are marked with ``featured=True``, there are
several useful tools:

* :py:meth:`Lookup.objects.featured_lookups_for(newsitem, name) <LookupManager.featured_lookups_for>`
  will, given a NewsItem instance and an attribute name, find all
  featured Lookups for that attribute which are relevant to that NewsItem.
* The same functionality is available in templates via the 
  :py:func:`featured_lookups_for_item <ebpub.db.templatetags.eb.featured_lookups_for_item>` template tag.
* :py:func:`get_featured_lookups_by_schema <ebpub.db.templatetags.eb.get_featured_lookups_by_schema>`
  is a tag that finds all currently featured Lookups, and URLs to find
  relevant NewsItems.


.. _charting_and_filtering:

Charting and filtering lookups
------------------------------

Set ``SchemaField.is_filter=True`` on a lookup SchemaField, and the detail page for
the NewsItem (newsitem_detail) will automatically link that field to a page
that lists all of the other NewsItems in that Schema with that particular
Lookup value.

Set ``SchemaField.is_charted=True`` on a lookup SchemaField, and the detail page
for the Schema (schema_detail) will include a chart of the top 10 lookup values
in the last 30 days' worth of data. Similar charts are on the
place detail overview page. (This assumes aggregates are populated; see
the Aggregates section below.)


module contents
================
"""

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.db.models import Count
from django.core import urlresolvers
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from ebpub.db import constants
from ebpub.geocoder.parser.parsing import normalize
from ebpub.utils.geodjango import flatten_geomcollection
from ebpub.utils.geodjango import ensure_valid
from ebpub.utils.text import slugify
from .fields import OpenblockImageField

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
    Example return value::

        {1: {u'crime_type': 'varchar01', u'crime_date', 'date01'},
         2: {u'permit_number': 'int01', 'to_date': 'date01'},
        }
    """
    result = {}
    for sf in SchemaField.objects.filter(schema__id__in=(schema_id_list)).values('schema', 'name', 'real_name'):
        result.setdefault(sf['schema'], {})[sf['name']] = sf['real_name']
    return result


class SchemaQuerySet(models.query.GeoQuerySet):

    def update(self, *args, **kwargs):
        # Django doesn't provide pre/post_update signals, rats.
        # See https://code.djangoproject.com/ticket/13021
        # So we define one and send it here.
        result = super(SchemaQuerySet, self).update(*args, **kwargs)
        post_update.send(sender=Schema)
        return result


class SchemaManager(models.Manager):

    _allowed_ids_cache_key = 'allowed_schema_ids__all'

    def update(self, *args, **kwargs):
        return self.get_query_set().update(*args, **kwargs)

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def get_query_set(self):
        """Warning: This breaks manage.py dumpdata.
        See bug #82.

        """
        return SchemaQuerySet(model=self.model, using=self._db).defer(
            'short_description',
            'summary',
            'source',
            'short_source',
            'update_frequency',
            )

    def allowed_schema_ids(self):
        """
        Useful for filtering out schemas (or things related to
        schemas) based on the current Manager.
        """
        ids = cache.get(self._allowed_ids_cache_key, None)
        if ids is None:
            ids = [s['id'] for s in self.all().values('id')]
            cache.set(self._allowed_ids_cache_key, ids, constants.ALLOWED_IDS_CACHE_TIME)
        return ids


class SchemaPublicManager(SchemaManager):

    _allowed_ids_cache_key = 'allowed_schema_ids__public'

    def get_query_set(self):
        return super(SchemaManager, self).get_query_set().filter(is_public=True)


class Schema(models.Model):
    """
    Describes a type of :py:class:`NewsItem`.  A NewsItem has exactly one Schema,
    which describes its Attributes, via associated :py:class:`SchemaFields <SchemaField>`.

    nb. to get all NewsItem instances for a Schema, you can do the usual as per
    http://docs.djangoproject.com/en/dev/topics/db/queries/#backwards-related-objects:
    schema.newsitem_set.all()

    nb. Some Schemas may not be visible to some users, if eg.
    ``is_public=False``. To abstract this, use the
    :py:func:`ebpub.utils.view_utils.get_schema_manager` function,
    rather than directly using ``Schema.objects`` or ``Schema.public_objects``.

    (To filter NewsItems appropriately, do NewsItem.objects.by_request(request)
    which will take care of using the right Schema manager.)
    """
    name = models.CharField(max_length=32)
    plural_name = models.CharField(max_length=32)
    indefinite_article = models.CharField(max_length=2,
                                          help_text="eg.'a' or 'an'")
    slug = models.SlugField(max_length=32, unique=True)
    min_date = models.DateField(
        help_text="The earliest available pub_date for this Schema",
        default=lambda: datetime.date(1970, 1, 1))
    last_updated = models.DateField(
        help_text=u"Last date any NewsItems were loaded for this Schema.")
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

    allow_flagging = models.BooleanField(
        default=False,
        help_text="Whether to allow users to flag NewsItems of this schema as spam or inappropriate."
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

    # TODO: maybe this should be either a FileField or a FilePathField instead?
    map_icon_url = models.TextField(
        blank=True, null=True,
        help_text="Set this to a URL to a small image icon and it will be displayed on maps. Should be roughly 40x40 pixels. Optional.",
        )

    def get_map_icon_url(self):
        # Could be relative.
        url = self.map_icon_url or u''
        if url and not (url.startswith('/') or url.startswith('http')):
            url = '%s/%s' % (settings.STATIC_URL.rstrip('/'), url)
        return url

    map_color = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="CSS color code used on maps to display this type of news. eg #FF0000.  Only used if map_icon_url is not set. Optional.")


    edit_window = models.FloatField(
        blank=True, default=0.0,
        help_text=u"How long, in hours, the creator of an item is allowed to edit it. Set to 0 to disallow edits by non-Admin users. Set to -1 to allow editing forever."
        )

    objects = SchemaManager()
    public_objects = SchemaPublicManager()

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)

    def get_absolute_url(self):
        return urlresolvers.reverse('ebpub-schema-filter', args=(self.slug,))

    # Backward compatibility.
    url = get_absolute_url

    ######################################################################
    # Metadata fields that used to live in a separate SchemaInfo model.
    short_description = models.TextField(blank=True, default='')
    summary = models.TextField(blank=True, default='')
    source = models.TextField(blank=True, default='',
                              help_text='Where this information came from, as one or more URLs, one per line.')
    short_source = models.CharField(max_length=128, blank=True, default='One-line description of where this information came from.')
    update_frequency = models.CharField(max_length=64, blank=True, default='',
                                        choices=FREQUENCY_CHOICES)

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
        blank=True, default=False,
        help_text='Whether the value is a foreign key to Lookup.'
        )
    is_filter = models.BooleanField(
        blank=True, default=False,
        help_text='Whether to link to list of items with the same value in this field. Assumes is_lookup=True.'
        )
    is_charted = models.BooleanField(
        blank=True, default=False,
        help_text='Whether the schema detail view displays a chart for this field; also see "trends" tabs on place overview page. Assumes is_lookup=True.'
        )
    display_order = models.SmallIntegerField(default=10)
    is_searchable = models.BooleanField(
        default=False,
        help_text="Whether the value is searchable by content. Doesn't make sense if is_lookup=True."
        )

    def natural_key(self):
        return (self.schema.slug, self.real_name)

    class Meta(object):
        unique_together = (('schema', 'real_name'),
                           ('schema', 'name'),
                           )
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
    '''
    Used for classifying and grouping :py:class:`Location`.
    
    You'll want to create at least one LocationType with the slug set to
    the same value as ``settings.DEFAULT_LOCTYPE_SLUG``, because that's
    used in various default URLs.  By default this is set to
    "neighborhoods".
    '''
    name = models.CharField(max_length=255,
                            help_text='for example, "Ward" or "Congressional District"')
    plural_name = models.CharField(max_length=64)
    scope = models.CharField(max_length=64,
                             help_text='e.g., "Chicago" or "U.S.A.". For display only; has no effect.')
    slug = models.SlugField(max_length=32, unique=True)
    is_browsable = models.BooleanField(
        default=True, help_text="Whether this is displayed on location_type_list.") #  XXX unused??
    is_significant = models.BooleanField(
        default=True,
        help_text="Whether this can be used to filter NewsItems, shows up in 'nearby locations', etc."
        )

    def __unicode__(self):
        return u'%s, %s' % (self.name, self.scope)

    def get_absolute_url(self):
        return urlresolvers.reverse('ebpub-loc-type-detail', args=(self.slug,))

    # Backward compatibility.
    url = get_absolute_url

    def natural_key(self):
        return (self.slug,)

    class Meta:
        ordering = ('name',)

    objects = LocationTypeManager()


class LocationManager(models.GeoManager):
    def get_by_natural_key(self, slug, location_type_slug):
        return self.get(slug=slug, location_type__slug=location_type_slug)


class Location(models.Model):
    '''
    A polygon that represents a geographic area, such as a specific
    neighborhood, ZIP code boundary or political boundary. Each ``Location`` has an
    associated :py:class:`LocationType` (e.g., "neighborhood"). To add a Location to the
    system, follow these steps:

        1. Create a :py:class:`LocationType`.

        2. Get the Location's geographic representation (a set of
           longitude/latitude points that determine the border of the
           polygon).  You might want to draw this on your own using
           desktop GIS tools or online tools, or you can try to get
           the data from a company or government agency.  (You can
           even draw simple shapes in the OpenBlock admin UI.)

        3. With the geographic representation, create a row in the
           "db_location" table that describes the Location. See below
           for what the various fields mean.

           You can create Locations in various ways: use the admin UI;
           use the script ``add_location`` to create one by
           specifying its geometry in well-known text (WKT) format;
           use the script ``import_locations`` to import them from shapefiles;
           or use the Django model API; or do a manual SQL INSERT statement.
    '''

    name = models.CharField(max_length=255, help_text='e.g., "35th Ward"')
    normalized_name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=32, db_index=True)
    location_type = models.ForeignKey(LocationType)
    location = models.GeometryField(null=True)
    display_order = models.SmallIntegerField()
    city = models.CharField(max_length=255, db_index=True)
    source = models.CharField(max_length=64)
    area = models.FloatField(
        blank=True, null=True,
        help_text="In square meters. This is populated automatically."
        # the db trigger is created by ebpub/db/migrations/0004_st_intersects_patch.py.
        )
    population = models.IntegerField(blank=True, null=True,
                                     help_text='Optional. If used, typicall found in census data.')
    user_id = models.IntegerField(
        blank=True, null=True,
        help_text="Used for 'custom' Locations created by end users.")
    is_public = models.BooleanField(
        help_text='Whether this is publically visible, or requires the staff cookie')
    description = models.TextField(blank=True)
    creation_date = models.DateTimeField(blank=True, null=True,
                                         default=datetime.datetime.now)
    last_mod_date = models.DateTimeField(blank=True, null=True,
                                         default=datetime.datetime.now)

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

    def get_absolute_url(self):
        return urlresolvers.reverse('ebpub-location-recent',
                                    args=(self.location_type.slug, self.slug))

    # Backward compatibility.
    url = get_absolute_url

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
    Represents an alternate name for a :py:class:`Location`.
    """
    pretty_name = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255, db_index=True)
    location = models.ForeignKey(Location,
                                 help_text='Location this is a synonym for.')
    objects = LocationSynonymManager()

    def save(self, force_insert=False, force_update=False, using=None):
        # Not doing this in clean() because we really don't want there to be
        # any way to get this wrong.
        if self.normalized_name:
            self.normalized_name = normalize(self.normalized_name)
        else:
            self.normalized_name = normalize(self.pretty_name)
        super(LocationSynonym, self).save(force_update=force_update, force_insert=force_insert, using=using)

    def __unicode__(self):
        return self.pretty_name


class AttributesDescriptor(object):

    # No docstring, not part of API.
    #
    # This class provides the functionality that makes the attributes available
    # as a dictionary-like `attributes` on a model instance.
    #
    # You normally don't instantiate this directly.
    # Just use newsitem.attributes like a normal dictionary.

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

    # No docstring, not part of API.
    #
    # A dictionary-like object that serves as a wrapper around attributes for a
    # given NewsItem.
    #
    # You normally don't instantiate this directly.
    # Just use news_item.attributes like a normal dictionary.

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
        # TODO: refactor, code overlaps largely with AttributesDescriptor.__set__
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

    """
    Adds special methods for searching :py:class:`NewsItem`.
    """

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
        SchemaField is att_value.

        For example::

           items = NewsItem.objects.filter(schema_id=1)
           sf = SchemaField.objects.get(name='violation', schema_id=1)
           items.by_attribute(sf, 'unsanitary work surface')

        If att_value is a list, this will do the
        equivalent of an "OR" search, returning all NewsItems that have an
        attribute value in the att_value list.

        Handles many-to-many lookups correctly behind the scenes.

        If is_lookup is True, then each att_value must be either a
        :py:class:`Lookup` instance, or the 'code' field of a Lookup instance, or an id
        of a Lookup instance.  (If is_lookup is False, then only ids
        will work.)

        Does not support comparisons other than simple equality testing.
        """

        clone = self.prepare_attribute_qs()
        real_name = str(schema_field.real_name)
        if isinstance(att_value, models.query.QuerySet):
            att_value = list(att_value)
        if not isinstance(att_value, (list, tuple)):
            att_value = [att_value]
        if is_lookup:
            if isinstance(att_value[0], int):
                # Assume all are Lookup.id values. Get just the ones
                # that exist.
                att_value = Lookup.objects.filter(schema_field__id=schema_field.id, id__in=att_value)
            elif not isinstance(att_value[0], Lookup):
                # Assume all are Lookup.code values. Get just the ones
                # that exist.
                att_value = Lookup.objects.filter(schema_field__id=schema_field.id, code__in=att_value)
            if not att_value:
                # If the lookup values don't exist, then there aren't any
                # NewsItems with these attribute values. Note that we aren't
                # using QuerySet.none() here, because we want the result to
                # be a NewsItemQuerySet, and none() returns a normal QuerySet.
                clone = clone.extra(where=('1=0',))
                return clone
            att_value = [val.id for val in att_value]
        if schema_field.is_many_to_many_lookup():
            for value in att_value:
                if not str(value).isdigit():
                    raise ValueError('Only integer strings allowed for att_value in many-to-many SchemaFields; got %r' % value)
            # We have to use a regular expression search to look for
            # all rows with the given att_value *somewhere* in the
            # column. The [[:<:]] thing is a word boundary, and the
            # (?:) groups the possible values to distinguish them from
            # the word boundary part of the regex.
            pattern = '[[:<:]](?:%s)[[:>:]]' % '|'.join([str(val) for val in att_value])
            clone = clone.extra(where=("db_attribute.%s ~ '%s'" % (real_name, pattern),))

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
        Returns a dictionary mapping {item_date: count}, i.e. the number of
        :py:class:`NewsItem` created each day.
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

    def by_request(self, request):
        """
        Returns a QuerySet that does additional request-specific
        filtering; currently this just uses
        get_schema_manager(request) to limit the schemas that are
        visible during this request.
        """
        clone = self._clone()
        from ebpub.utils.view_utils import get_schema_manager
        allowed_schema_ids = get_schema_manager(request).allowed_schema_ids()
        return clone.filter(schema__id__in=allowed_schema_ids)


class NewsItemManager(models.GeoManager):
    """
    Available as :py:class:`NewsItem`.objects
    """
    def get_query_set(self):
        """
        Returns a :py:class:`NewsItemQuerySet`
        """
        return NewsItemQuerySet(self.model)

    def by_attribute(self, *args, **kwargs):
        """
        See :py:meth:`NewsItemQuerySet.by_attribute`
        """
        return self.get_query_set().by_attribute(*args, **kwargs)

    def text_search(self, *args, **kwargs):
        """
        See :py:meth:`NewsItemQuerySet.text_search`
        """
        return self.get_query_set().text_search(*args, **kwargs)

    def date_counts(self, *args, **kwargs):
        """
        See :py:meth:`NewsItemQuerySet.date_counts`
        """
        return self.get_query_set().date_counts(*args, **kwargs)

    def top_lookups(self, *args, **kwargs):
        """
        See :py:meth:`NewsItemQuerySet.top_lookups`
        """
        return self.get_query_set().top_lookups(*args, **kwargs)

    def by_request(self, request):
        """
        See :py:meth:`NewsItemQuerySet.by_request`
        """
        return self.get_query_set().by_request(request)


class NewsItem(models.Model):
    """
    A NewsItem is broadly defined as "something with a date and a
    location." For example, it could be a local news article, a
    building permit, a crime report, or a photo.

    For the big picture, see :ref:`newsitems`


    """

    # We don't have a natural_key() method because we don't know for
    # sure that anything other than ID will be unique.

    schema = models.ForeignKey(Schema, help_text=u'What kind of news is this and what extra fields does it have?')
    title = models.CharField(max_length=255, help_text=u'the "headline"')
    description = models.TextField(blank=True, default=u'')
    url = models.TextField(
        blank=True, default=u'',
        help_text="link to original source for this news")
    pub_date = models.DateTimeField(
        db_index=True,
        help_text='Date/time this Item was added to the OpenBlock site; default now.',
        default=datetime.datetime.now,
        blank=True,
        )
    item_date = models.DateField(
        db_index=True,
        help_text='Date (without time) this Item occurred, or failing that, the date of publication on the original source site; default today.',
        default=datetime.date.today,
        blank=True,
        )

    # Automatic last modification tracking.  Note: if changing only attributes, the
    # NewsItem should also be save()'d to update last_modification when complete.
    last_modification = models.DateTimeField(db_index=True, auto_now=True)

    location = models.GeometryField(blank=True, null=True, spatial_index=True,
                                    help_text="Coordinates where this news occurred.")
    location_name = models.CharField(max_length=255,
                                     help_text="Human-readable address or name of place where this news item occurred.")
    location_object = models.ForeignKey(Location, blank=True, null=True,
                                        help_text="Optional reference to a Location where this item occurred, for use when we know the general area but not specific coordinates.",
                                        related_name='+')

    location_set = models.ManyToManyField(
        Location, through='NewsItemLocation', blank=True, null=True,
        help_text="db.Location objects that intersect with our .location geometry. These are set automatically, do not try to assign to them.")

    objects = NewsItemManager()

    # Treat this like a dict. The related Schema and SchemaFields explain
    # what keys/ types of values you can set.
    # See the ``ebpub`` section of the docs for more information.
    # Note you do NOT need to save() the NewsItem after setting or modifying
    # this dictionary - but you do need to save() before the FIRST time you do so,
    # because the underlying Attribute instance needs a reference to the NewsItem's
    # primary key.
    attributes = AttributesDescriptor()

    def clean(self):
        if self.location is None:
            if self.location_object is None:
                logger.warn(
                    "Saving NewsItem with neither a location nor a location_object")
        else:
            self.location = ensure_valid(flatten_geomcollection(self.location))

    class Meta:
        ordering = ('title',)

    def __unicode__(self):
        return self.title or 'Untitled News Item'

    def get_absolute_url(self):
        return urlresolvers.reverse('ebpub-newsitem-detail',
                                    args=[self.schema.slug, self.id], kwargs={})

    # Backward compatibility.
    item_url = get_absolute_url

    def item_url_with_domain(self):
        return 'http://%s%s' % (settings.EB_DOMAIN, self.item_url())

    def item_date_url(self):
        from ebpub.db.schemafilters import FilterChain
        chain = FilterChain(schema=self.schema)
        chain.add('date', self.item_date)
        return chain.make_url()

    def location_url(self):
        if self.location_object_id is not None:
            return self.location_object.url()
        # TODO: look for a Block?
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
            # Hopefully we can cope with an empty dict.
            #return []
        return [AttributeForTemplate(f, self.attributes) for f in fields]


class AttributeForTemplate(object):
    def __init__(self, schema_field, attribute_row):
        self.sf = schema_field
        if not schema_field.name in attribute_row:
            logger.warn("Attribute row %s is missing field %s" %
                        (attribute_row, schema_field.name))
        self.raw_value = attribute_row.get(schema_field.name)
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
                    self.values = [lookups[i] for i in id_values if i in lookups]
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
    that NewsItem.

    You don't normally access an Attribute instance directly.
    You usually go through the dictionary-like API provided by
    :ref:`newsitem_attributes`.

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

    def get_by_natural_key(self, slug, schema__slug,
                           schema_field__real_name):
        return self.get(slug=slug, schema_field__schema__slug=schema__slug,
                        schema_field__real_name=schema_field__real_name)

    def get_or_create_lookup(self, schema_field, name, code=None, description='', make_text_slug=True, logger=None):
        """
        Returns the Lookup instance matching the given SchemaField, name and
        Lookup.code, creating it (with the given name/code/description) if it
        doesn't already exist.

        If ``code`` is not provided, ``name`` will be also used as code.

        If ``make_text_slug`` is True (the default), then a slug will
        be created from the given name. If it's False, then the slug
        will be the Lookup's ID.
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
            if Lookup.objects.filter(schema_field=schema_field, name=name).count():
                # Avoid integrity errors on 'name'.
                old_name = name
                name = name + ' b'
                log_warn("Munging name %r to %r in order to avoid dupe." % (old_name, name))

            obj = Lookup(schema_field_id=schema_field.id, name=name, code=code, slug=slug, description=description)
            obj.save()
            if not make_text_slug:
                # Set the slug to the ID.
                obj.slug = obj.id
                obj.save()
            log_info('Created %s %r' % (schema_field.name, name))
        return obj

    def featured_lookups_for(self, newsitem, attribute_key):
        """
        Return a list of the :ref:`featured_lookups` that the
        newsitem has for the named attribute.

        Here's a rather morbid example::

          schema = Schema(name='obituary', ...)
          profession = SchemaField(schema=schema, is_lookup=True, name="profession")

        Now let's make some lookups representing a few professions::

          nurse = Lookup(schema_field=sf, name='nurse')
          programmer = Lookup(schema_field=sf, name='programmer')
          chef = Lookup(schema_field=sf, name='chef')

        And some NewsItems::

          item1 = NewsItem(schema=schema, ...)
          item1.attributes['profession'] = programmer.id

        And let's imagine that this week, we are very excited about
        recently deceased programmers::

           programmer.featured = True
           programmer.save()

        Now we can use ``featured_lookups_for`` to see if this person
        was a programmer::

          for feat in Lookup.objects.featured_lookups_for(schema, item1):
              print feat.name
          # --> prints "programmer"

        If we disable the ``featured`` flag on the Lookup, because
        people have lost interest in deceased programmers, then
        getting featured lookups on this programmer returns an empty
        list::

          programmer.featured = False
          programmer.save()
          for feat in Lookup.objects.featured_lookups_for(schema, item1):
              print feat.name
          # --> prints nothing.

        See also the
        :py:func:`featured_lookups_for_item <ebpub.db.templatetags.eb.featured_lookups_for_item>`
        template tag.

        """
        # This uses several queries, not very efficient...
        sf = SchemaField.objects.get(schema__id=newsitem.schema_id, name=attribute_key)
        # Yet another manual decode of the comma-separated value,
        # refs #265
        if sf.is_many_to_many_lookup():
            try:
                value = newsitem.attributes.get(attribute_key, None)
                if not value:
                    ni_lookup_ids = []
                else:
                    ni_lookup_ids = [int(i) for i in value.split(',')]
            except (KeyError, AttributeError):
                # This item may be lacking an Attributes row entirely?
                # Or the value may be None.
                # Not sure when/how that happens, but it'll get fixed
                # on any write to item.attributes, so don't worry
                # about it here.
                ni_lookup_ids = []
        else:
            ni_lookup_ids = [newsitem.attributes[attribute_key]]
        featured = self.filter(featured=True, id__in=ni_lookup_ids)
        return featured


class Lookup(models.Model):
    """
    Lookups are a normalized way to store Attribute fields that have only a
    few possible values.

    For more context, see :ref:`lookups`.
    """
    schema_field = models.ForeignKey(
        SchemaField,
        help_text="This must be a SchemaField whose real_name is an int or varchar column.")
    name = models.CharField(max_length=255,
                            help_text='Human-readable name of this lookup value.')
    code = models.CharField(
        max_length=255, blank=True,
        help_text='Value used for queries. May differ from `name` if `name` is modified from the original data source, eg. to make `name` prettier. `code` should not be modified from the original source data.',
        db_index=True)
    # ... For example, in scraping Chicago crimes, we use the crime type code
    # to find the appropriate crime type in this table. We can't use `name`
    # in that case, because we've massaged `name` to use a "prettier"
    # formatting than exists in the data source.

    slug = models.SlugField(max_length=32, db_index=True,
                            help_text="URL-safe identifier")
    description = models.TextField(blank=True)

    featured = models.BooleanField(blank=True, default=False,
                                   help_text="Whether this lookup value is 'special' eg. for use in navigation.")

    objects = LookupManager()

    class Meta:
        unique_together = (('slug', 'schema_field'),
                           ('code', 'schema_field'),
                           ('name', 'schema_field'),
                          )
        ordering = ('slug',)

    def natural_key(self):
        return (self.slug, self.schema_field.schema.slug,
                self.schema_field.real_name)

    def __unicode__(self):
        return u'%s - %s' % (self.schema_field, self.name)


class NewsItemLocation(models.Model):
    """

    Many-to-many mapping of :py:class:`NewsItem` to
    :py:class:`Location` where the geometries intersect.

    This is both an optimization - so we don't have to do spatial
    searches very much - and a useful abstraction in that a NewsItem
    may be relevant in any number of places.
    You can get all associated Locations from a
    NewsItem by doing ``newsitem.location_set.all()``, and all associated
    NewsItems from a Location by doing ``location.newsitem_set.all()``.

    Normally you don't have to worry about creating NewsItemLocations:
    there are database triggers that update this table whenever a
    NewsItem's location is set or updated.

    """
    news_item = models.ForeignKey(NewsItem)
    location = models.ForeignKey(Location)

    class Meta:
        unique_together = (('news_item', 'location'),)

    def __unicode__(self):
        return u'%s - %s' % (self.news_item, self.location)


#############################################################################
# Aggregates.

class AggregateBaseClass(models.Model):
    """
    Aggregates provide for quick lookups of NewsItems by various buckets,
    eg. number of NewsItems added on one day.
    """
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


class NewsItemImage(models.Model):
    """
    NewsItems can optionally be associated with any number of images.
    """

    news_item = models.ForeignKey(NewsItem)
    # Note max_length = filename.
    image = OpenblockImageField(upload_to=settings.MEDIA_ROOT, max_length=256,
                                help_text='Upload an image')

    class Meta(object):
        unique_together = (('news_item', 'image'),)

    def __unicode__(self):
        return u'%s - %s' % (self.news_item, self.image.name)

###########################################
# Signals                                 #
###########################################

# Django doesn't provide a pre_update() signal, rats.
# See https://code.djangoproject.com/ticket/13021
from django.dispatch import Signal
from django.db.models.signals import post_save, post_delete

post_update = Signal(providing_args=[])

def clear_allowed_schema_ids_cache(sender, **kwargs):
    cache.delete_many((SchemaPublicManager._allowed_ids_cache_key,
                       SchemaManager._allowed_ids_cache_key))

post_update.connect(clear_allowed_schema_ids_cache, sender=Schema)
post_save.connect(clear_allowed_schema_ids_cache, sender=Schema)
post_delete.connect(clear_allowed_schema_ids_cache, sender=Schema)

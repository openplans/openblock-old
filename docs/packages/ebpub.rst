=====
ebpub
=====

Publishing system for block-specific news, as used by EveryBlock.com.

Before you dive in, it's *highly* recommend you spend a little bit of time
browsing around EveryBlock.com to get a feel for what this software does.

Also, for a light conceptual background on some of this, particularly the
data storage aspect, watch the video "Behind the scenes of EveryBlock.com"
here: http://blip.tv/file/1957362

Settings
========

ebpub requires a smorgasbord of eb-specific settings in your settings
file.  If you follow the :doc:`../custom` or :doc:`obdemo`
directions, they provide suitable settings files that you can
adjust as needed.  Otherwise, you might just start with the file
ebpub/settings.py and tweak that (or import from it in your own
settings file). The application won't work until you set the
following::

       DATABASE_USER
       DATABASE_NAME
       DATABASE_HOST
       DATABASE_PORT
       SHORT_NAME
       PASSWORD_CREATE_SALT
       PASSWORD_RESET_SALT
       METRO_LIST
       EB_MEDIA_ROOT
       EB_MEDIA_URL
       EB_DOMAIN
       DEFAULT_MAP_CENTER_LON
       DEFAULT_MAP_CENTER_LAT
       DEFAULT_MAP_ZOOM

======
Models
======

Broadly speaking, the system requires two different types of data:
geographic boundaries (Locations, Streets, Blocks and Intersections)
and news (Schemas and NewsItems).

.. _geomodels:

Geographic Models
=================

.. _locations:

LocationTypes / Locations
-------------------------

A ``Location`` is a polygon that represents a geographic area, such as a specific
neighborhood, ZIP code boundary or political boundary. Each ``Location`` has an
associated ``LocationType`` (e.g., "neighborhood"). To add a Location to the
system, follow these steps:

    1. Create a row in the "db_locationtype" table that describes this
       LocationType. See the LocationType model code in ``ebpub/db/models.py`` for
       information on the fields and what they mean.

    2. Get the Location's geographic representation (a set of
       longitude/latitude points that determine the border of the polygon).
       You might want to draw this on your own using desktop GIS tools or
       online tools, or you can try to get the data from a company or
       government agency.

    3. With the geographic representation, create a row in the "db_location"
       table that describes the Location. See the Location model code in
       ebpub/db/models.py for information on the fields and what they mean.
       You can use the script ebpub/db/bin/add_location.py, use the Django
       database API or do a manual SQL INSERT statement.

You'll need to create at least one LocationType with the slug "neighborhoods",
because that's hard-coded in various places throughout the application.

.. _blocks:

Blocks
------

A Block is a segment of a single street between one side street and another
side street. Blocks are a fundamental piece of the ebpub system; they're used
both in creating a page for each block and in geocoding.

Blocks are stored in a database table called "blocks". To populate this table,
follow these steps:

    1. Obtain a database of the streets in your city, along with each street's
       address ranges and individual street segments. If you live in the
       U.S.A. and your city hasn't had much new development since the year
       2000, you might want to use the U.S. Census' TIGER/Line file
       (http://www.census.gov/geo/www/tiger/).

    2. Import the streets data into the "blocks" table. ebpub provides two
       pre-made import scripts:

           * If you're using TIGER/Line data, you can use the script
             ``ebpub/streets/blockimport/tiger/import_blocks.py.``

           * If you're using data from ESRI, you can use the script
	     ``ebpub/streets/blockimport/esri/importers/blocks.py.``

           * If you're using data from another source, take a look at the
             Block model in ``ebpub/streets/models.py`` for all of the required
             fields.

Streets and Intersections
--------------------------

The ebpub system maintains a separate table of each street in the city. Once
you've populated the blocks, you can automatically populate the streets table
by running the importer ``ebpub/streets/populate_streets.py.``

The ebpub system also maintains a table of each intersection in the city, where
an intersection is defined as the meeting point of two streets. Just like
streets, you can automatically populate the intersections table by running the
code in ``ebpub/streets/populate_streets.py.``

Streets and intersections are both necessary for various bits of the site to
work, such as the "browse by street" navigation and the geocoder (which
supports the geocoding of intersections).

Once you've got all of the above geographic boundary data imported, you can
verify it on the site by going to /streets/ and /locations/.

.. _newsitem-schemas:

NewsItems and Schemas
=====================

Next, it's time to start adding news. The ebpub system is capable of handling
many disparate types of news -- e.g., crime, photos and restaurant inspections.
Each type of news is referred to as a ``Schema``.

To add a new Schema, add a row to the "db_schema" database table or
use the Django database API. See the :doc:`../schemas` documentation, or
see the ``Schema`` model in
``ebpub/db/models.py`` for information on all of the fields

.. _newsitems:

NewsItems
---------

A ``NewsItem`` is broadly defined as "something with a date and a location." For
example, it could be a building permit, a crime report, or a photo. NewsItems
are stored in the "db_newsitem" database table, and they have the following
fields:

    schema
      the associated Schema object

    title
      the "headline"

    description
      an optional blurb describing what happened

    url
      an optional URL to another Web site

    pub_date
      the date this NewsItem was added to the site

    item_date
      the date of the object

    location
      the location of the object (a GeoDjango GeometryField, usually a
      Point)

    location_name
      a textual representation of the location, eg. an address or
      place name

    location_object
      an optional associated Location object

    block
      an optional associated Block object

    attributes
      extensible metadata, described in the section on
      `SchemaFields and Attributes`_.

The difference between ``pub_date`` and ``item_date`` might be confusing. The
distinction is intended for data sets where there's a lag in publishing or
where the data is updated infrequently or irregularly. For example, on
EveryBlock.com, Chicago crime data is published a week after it is reported,
so a crime's item_date is the day of the crime report whereas the pub_date
is the day the data was published to EveryBlock.com (generally seven days after
the item_date).

Similarly, ``location_object`` and ``location`` can be
confusing. ``location_object`` is used rarely; a good use case would
be some police blotter reports which don't provide precise location
information for a news item other than which precinct it occurs in.
In this case, you'd want a LocationType representing precincts,
and a Location for each precinct; then, when creating a
NewsItem, set its ``location_object`` to the relevant Location, and don't
set ``location`` or ``block`` at all.  For a live example, see
http://nyc.everyblock.com/crime/by-date/2010/8/23/3364632/


NewsItemLocations
------------------

This model simply maps any number of NewsItems to any number of
Locations. The rationale is that locations may overlap, so a NewsItem
may be relevant in any number of places.  Normally you don't have to
worry about this: there are database triggers that update this table
whenever a NewsItem's location is set or updated.


.. _ebpub-schemas:

SchemaFields and Attributes
---------------------------

The NewsItem model in itself is generic -- a lowest-common denominator of each
NewsItem on the site. If you'd like to extend your NewsItems to include
Schema-specific attributes, you can use SchemaFields and Attributes.

A single NewsItem is described by one NewsItem instance, one
corresponding Attribute instance containing metadata, and one Schema
that identifies the "type" of NewsItem. The Schema in turn is
described by a number of SchemaFields which describe the meaning of
the fields of Attribute instances for this type of NewsItem.

Or, from a database perspective: The "db_attribute" table stores
arbitrary attributes for each NewsItem, and the "db_schemafield" table
is the key for those attributes. A SchemaField says, for example, that
the "int01" column in the db_attribute table for the "real estate
sales" Schema corresponds to the "sale price".

This can be confusing, so here's an example. Say you have a "real estate sales"
Schema, with an id of 5. Say, for each sale, you have the following
information:

    address

    sale date

    sale price

    property type (single-family home, condo, etc.)

The first two fields should go in NewsItem.location_name and NewsItem.item_date,
respectively -- there's no reason to put them in the Attribute table, because
the NewsItem table has a slot for them.

Sale price is a number (we'll assume it's an integer), so create a SchemaField
defining it:

    schema_id = 5
        The id of our "real estate sales" schema.

    name = 'sale_price'
        The alphanumeric-and-underscores-only name for this field. (Used in URLs.)

    real_name = 'int01'
        The column to use in the db_attribute model. Choices are:
        int01-07, text01, bool01-05, datetime01-04, date01-05, time01-02,
        varchar01-05. This value must be unique with respect to the schema_id.

    pretty_name = 'sale price'
        The human-readable name for this attribute.

    pretty_name_plural = 'sale prices'
        The plural human-readable name for this attribute.

    display = True
        Whether to display the value on the site.

    is_lookup = False
        Whether it's a lookup. (Don't worry about this for now; see the Lookups
        section below.)

    is_filter = False
        Whether it's a filter. (Again, don't worry about this for now.)

    is_charted = False
        Whether it's charted. (Again, don't worry.)

    display_order = 1
        An integer representing what order it should be displayed in on
        newsitem_detail pages.

    is_searchable = False
        Whether it's searchable. This only applies to textual fields (varchars
        and texts).

Once you've created this SchemaField, the value of "int01" for any db_attribute
row with schema_id=5 will be the sale price.

.. _lookups:

Lookups
-------

Lookups are a normalized way to store attributes that have only a few
possible values.

Consider the "property type" data we have for each real estate sale
NewsItem in the example above.
We could store it as a varchar field (in which case we'd set
real_name='varchar01') -- but that would cause a lot of duplication and
redundancy, because there are only a couple of property types -- the set
['single-family', 'condo', 'land', 'multi-family']. To represent this set,
we can use a Lookup -- a way to normalize the data.

To do this, set ``SchemaField.is_lookup=True`` and make sure to use an 'int' column
for SchemaField.real_name. Then, for each record, get or create a Lookup
object (see the model in ``ebpub/db/models.py``) that represents the data, and use
the Lookup's id in the appropriate db_attribute column. The helper function
``Lookup.get_or_create_lookup()`` is a convenient shortcut here (see the
code/docstring of that function).

Many-to-many Lookups
--------------------

Sometimes a NewsItem has multiple values for a single attribute. For example, a
restaurant inspection can have multiple violations. In this case, you can use a
many-to-many Lookup. To do this, just set ``SchemaField.is_lookup=True`` as before,
but use a varchar field for the ``SchemaField.real_name``. Then, in the
db_attribute column, set the value to a string of comma-separated integers of
the Lookup IDs.

Charting and filtering lookups
------------------------------

Set ``SchemaField.is_filter=True`` on a lookup SchemaField, and the detail page for
the NewsItem (newsitem_detail) will automatically link that field to a page
that lists all of the other NewsItems in that Schema with that particular
Lookup value.

Set ``SchemaField.is_charted=True`` on a lookup SchemaField, and the detail page
for the Schema (schema_detail) will include a chart of the top 10 lookup values
in the last 30 days' worth of data. (This assumes aggregates are populated; see
the Aggregates section below.)

Aggregates
----------

Several parts of ebpub display aggregate totals of NewsItems for a particular
Schema. Because these calculations can be expensive, there's an infrastructure
for caching the aggregate numbers regularly in separate tables (db_aggregate*).

To do this, just run ebpub/db/bin/update_aggregates.py.

You'll want to do this on a regular basis, depending on how often you update
your data. Some parts of the site (such as charts) will not be visible until
you populate the aggregates.

.. _custom-look-feel:

Site views/templates
====================

Once you've gotten some data into your site, you can use the site to browse it
in various ways. The system offers two primary axes by which to browse the
data:

    * By schema -- starting with the schema_detail view/template
    * By place -- starting with the place_detail view/template (where a "place"
      is defined as either a Block or Location)

Note that default templates are included in ebpub/templates. At the very least,
you'll want to override base.html to design your ebpub-powered site. (The
design of EveryBlock.com is copyrighted; you'll have to come up with your own
unique look-and-feel.)

Custom NewsItem lists
---------------------

When NewsItems are displayed as lists, generally templates should use the
newsitem_list_by_schema custom tag. This tag takes a list of NewsItems (in
which it is assumed that the NewsItems are ordered by schema) and renders them
through separate templates, depending on the schema. These templates should be
defined in the ebpub/templates/db/snippets/newsitem_list directory and named
[schema_slug].html. If a template doesn't exist for a given schema, the tag
will use the template ebpub/templates/db/snippets/newsitem_list.html.

We've included two sample schema-specific newsitem_list templates,
news-articles.html and photos.html.

Custom NewsItem detail pages
----------------------------

Similarly to the newsitem_list snippets, you can customize the newsitem_detail
page on a per-schema basis. Just create a template named [schema_slug].html in
ebpub/templates/db/newsitem_detail. See the template
ebpub/templates/db/newsitem_detail.html for the default implementation.

Custom Schema detail pages
--------------------------

To customize the schema_detail page for a given schema, create a
``templates/db`` subfolder in your app, and add a template named
``[schema_slug].html`` in that directory. See the template
``ebpub/templates/db/schema_detail.html`` for the default generic
implementation.

.. _email_alerts:

E-mail alerts
=============

Users can sign up for e-mail alerts via a form on the place_detail
pages. To send the e-mail alerts, just run the ``send_all()`` function
in ``ebpub/alerts/sending.py``.  You probably want to do this
regularly by :doc:`../running_scrapers`.

Accounts
========

This system uses a customized version of Django's User objects and authentication
infrastructure. ebpub comes with its own User object and Django middleware that
sets request.user to the User if somebody's logged in.


=================================
Creating a Custom NewsItem Schema
=================================

In OpenBlock lingo, a *Schema* is a type of *NewsItem.* (It's a good
idea to read :ref:`concept_overview` if you haven't.)

OpenBlock's :doc:`../packages/ebpub` package provides several models
for defining Schemas.  This section provides a brief example of
creating a Schema, defining its optional custom fields, and creating a NewsItem
with the Schema.

It is assumed for this section that you have installed either
:doc:`the demo <../install/demo_setup>` or have created a :doc:`custom
application <../install/custom>`.

For background and additional detail, see also
:py:class:`ebpub.db.models.Schema` and :ref:`newsitem-schemas`
in the ebpub documentation, the code in ebpub.db.models and the 
video `"Behind the scenes of EveryBlock.com" <http://blip.tv/file/1957362>`_

.. admonition:: Cleaning Up After Experiments

  Typically it will take you a little while to settle on a schema you
  like, and you may accumulate some junk newsitems while testing.
  It's often useful to clean these up and start fresh. There is a
  script at ``ebpub/db/bin/delete_newsitems.py`` that can delete all
  NewsItems of a given Schema, plus all their Attributes and Lookups.
  Just specify the schema's slug.

Experimenting with Existing Schemas
-----------------------------------

When running `syncdb --migrate` with ``'ebpub'`` in
``settings.INSTALLED_APPS``, a few default schemas will be loaded for you:
a basic 'Local News' type, and an 'Open311 Service Requests' type.

If you also have :doc:`obdemo <../packages/obdemo>` in ``settings.INSTALLED_APPS``, you will get the
schemas that are used by our Boston demo, including: Boston events,
restaurant inspections, building permits, and Boston police reports.

You may wish to look at these in the admin UI to see how they're
configured.  Some of them might be appropriate for your purposes out
of the box or with slight modifications.

You can of course use the admin UI to delete any that you don't want
to use.

Note that modifications and deletions are permanent. We don't have an
"undo" feature, sorry.

Make a Schema From Scratch
--------------------------

For this example, we will model a "Crime Report".  Beyond the basic NewsItem information, 
like title, date, location etc, we will want to record some custom information with each report:

* Responding officer's name
* Type of crime (in english)
* Police code for crime

Steps are shown using the django shell, but this could also be performed in a script, or similar steps in the administrative interface.  This code can also be found in ``misc/examples/crime_report_schema.py``.  This section assumes your application is ``myblock``; substitute your own or ``obdemo`` for the demo application.  Start in the root of your virtual env:

.. code-block:: bash

    $ source bin/activate
    $ django-admin.py shell --settings=myblock.settings
    Python 2.6.1 (r261:67515, Feb 11 2010, 00:51:29) 
    [GCC 4.2.1 (Apple Inc. build 5646)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>> 

.. _creating_schema:

Creating the Schema
===================

The first step is to create an `ebpub.db.models.Schema` to represent the `Crime Report` type::

    >>> from ebpub.db.models import Schema
    >>> crime_report = Schema()

This object will contain metadata about all Crime Reports, like what its title is and how to pluralize it::
    
    >>> crime_report.indefinite_article = 'a'
    >>> crime_report.name = "Crime Report"
    >>> crime_report.plural_name = "Crime Reports"
    
The `slug` is the unique identifier for this Schema that will be used in URLs on the site.  It should be brief and contain URL safe characters::

    >>> crime_report.slug = 'crimereport'
    
The `min_date` field can be used to limit how far back the user can navigate when 
viewing crime reports.  For now, we'll just assume that everything is in the 
future::

    >>> from datetime import datetime
    >>> crime_report.min_date = datetime.utcnow()
    
The `last_updated` field tracks when we last checked for new crime reports. 
We'll also just stub this out to the current time for now::

    >>> crime_report.last_updated = datetime.utcnow()

The `has_newsitem_detail` field controls whether this item has a page hosted on this site, or whether it has its own external url.  We'll host these ourselves::

    >>> crime_report.has_newsitem_detail = True

Note that if your news source doesn't provide any URLs you can link
to, you will have to set this to True, or else clicking on links to
these items will result in a 404 Not Found error.

The `is_public` field controls whether or not NewsItems of this type are visible
to anybody other than administrators on the 
site.  Normally you should wait until the type is set up and loaded with 
news before "turning it on".  We'll just make it available immediately::

    >>> crime_report.is_public = True


The `is_event` field controls whether or not NewsItems of this type
are announcements of future events, rather than news that happened in
the past.  For more details on how to do this, see :ref:`future_events`
This doesn't apply to crime reports, so we'll leave it set to False:

    >>> crime_report.is_event = False

There are a few additional fields you can explore (see the code in ``ebpub.db.models.Schema``), but this will be good enough to 
start with.  So let's save it and move on::

    >>> crime_report.save()

At this point you will be able to see the type listed on your site's front page,
and reach an (empty) listing using your slug by visiting http://localhost:8000/crimereport
assuming you are running the web server.


Making Maps Prettier
====================

If you want your different NewsItem types to stand out from each other
on maps, you have two options.

You can set your schema's ``map_color`` to a hex color code
(eg. ``#FF0000``), and markers for that news type will be filled with
that color.

Or, you can set your schema's ``map_icon_url`` to the URL of an image
to use for its markers. Should be roughly 35x35 pixels.  (If you are
hosting your own map icons, it's fine to use a relative URL here.)

OpenBlock does not currently ship with any map icons.  One source of
good free (Creative Commons 3.0 BY-SA) map icons is
http://mapicons.nicolasmollet.com/ .


Adding Custom Fields
====================

.. admonition:: Do I need any custom fields at all?

   You might not.

   Some news sources will be simple enough that you don't need any
   extra fields.  If all you have is a title, date, URL, and maybe a
   description, you don't need extra fields.

   The key test for each piece of information is: Do I need this
   information, and does it fit into a plain vanilla ``NewsItem``?
   field?

   If the answers are "yes I need it but no it doesn't fit",
   then you need to create a SchemaField to describe this extra field.

   For a list of "core" NewsItem fields, see
   :py:class:`the NewsItem class documentation <ebpub.db.models.NewsItem>`.

As mentioned earlier, we will add the following custom fields:

* Responding officer's name
* Type of crime (in english)
* Police code for crime

We will create an ebpub.db.models.SchemaField to describe each custom field. Let's start with the reporting officer::

    >>> from ebpub.db.models import SchemaField
    >>> officer = SchemaField()
    >>> officer.schema = crime_report
    >>> officer.pretty_name = "Reporting Officer's Name"
    >>> officer.pretty_name_plural = "Reporting Officer's Names"

The values of *all* the custom fields for a particular NewsItem will be stored in a single 
``ebpub.db.models.Attribute`` object.  The Attribute object has a fixed set of fields
which can be used for custom attributes.  The fields are named according to their type, 
and numbered:

==============  ========  ===============================
 Names          Possible      Type
                Numbers
--------------  --------  -------------------------------
   varcharNN    01 - 05   models.CharField (length 255)
--------------  --------  -------------------------------
   dateNN       01 - 05   models.DateField
--------------  --------  -------------------------------
   timeNN       01 - 02   models.TimeField
--------------  --------  -------------------------------
   datetimeNN   01 - 04   models.DateTimeField
--------------  --------  -------------------------------
   boolNN       01 - 05   models.NullBooleanField
--------------  --------  -------------------------------
   intNN        01 - 07   models.IntegerField
--------------  --------  -------------------------------
   textNN       01        models.TextField
==============  ========  ===============================

Each SchemaField will map onto one of the fields of the Attribute class.  We'll map the reporting officer onto the first varchar field `varchar01` by setting the ``real_name`` attribute::

    >>> officer.real_name = 'varchar01'
    
When working with a crime report NewsItem, we'll want to have an alias
for this attribute in the code, so we don't always have to remember
what 'varchar01' means for crime reports.  This is set using the ``name`` field of the SchemaField.  We'll call it `officer`, and move on::

    >>> officer.name = 'officer'

That's the important stuff. There are a bunch of mandatory
display-related fields; we'll just gloss over these for now::

    >>> officer.display = True
    >>> officer.display_order = 10
    >>> officer.is_searchable = True
    >>> officer.is_lookup = False
    >>> officer.is_filter = False
    >>> officer.is_charted = False

Now we can save this SchemaField::

    >>> officer.save()
    
The name of the crime works the same way, but we'll need to store it
in a different field.  We'll use the second varchar field, `varchar02`::

    >>> crime_name = SchemaField()
    >>> crime_name.schema = crime_report
    >>> crime_name.real_name = "varchar02"
    >>> crime_name.pretty_name = "Crime Type"
    >>> crime_name.pretty_plural_name = "Crime Types"
    >>> crime_name.name = "crime_type"
    >>> crime_name.display = True
    >>> crime_name.display_order = 10
    >>> crime_name.is_searchable = True
    >>> crime_name.is_lookup = False
    >>> crime_name.is_filter = False
    >>> crime_name.is_charted = False
    >>> crime_name.save()
    
For the crime code, we'll use an integer field::

    >>> crime_code = SchemaField()
    >>> crime_code.schema = crime_report
    >>> crime_code.real_name = "int01"
    >>> crime_code.pretty_name = "Crime Code"
    >>> crime_code.pretty_plural_name = "Crime Codes"
    >>> crime_code.name = "crime_code"
    >>> crime_code.display = True
    >>> crime_code.display_order = 10
    >>> crime_code.is_searchable = True
    >>> crime_code.is_lookup = False
    >>> crime_code.is_filter = False
    >>> crime_code.is_charted = False
    >>> crime_code.save()

Phew, okay we just designed a NewsItem type!

Creating a NewsItem with the Schema
===================================

Now we can finally start churning out amazing crime reports.  We start by making a 
basic news item with our schema and filling out the basic fields::

    >>> from ebpub.db.models import NewsItem
    >>> report = NewsItem()
    >>> report.schema = crime_report
    >>> report.title = "Hooligans causing disturbance downtown"
    >>> report.location_name = "123 Fakey St."
    >>> report.item_date = datetime.utcnow()
    >>> report.pub_date = datetime.utcnow()
    >>> report.description = "Blah Blah Blah"
    >>> report.save()

Great, now (any only now) we can set the extra fields, which are weirdly immediately 
set when accessing the special ``attributes`` dictionary on the
NewsItem.  (There is some python magic going on, see the code in
``ebpub.db.models``.)  We use the names that we assigned when we were designing the schema: 

    >>> report.attributes['officer'] = "John Smith"
    >>> report.attributes['crime_type'] = "Disturbing The Peace"
    >>> report.attributes['crime_code'] = 187
    
If you visit the crime reports page at http://localhost:8000/crimereport it should list 
your new item.  You can click its link to view the custom details you added. 

Hooray!


Lookups: normalized enums
-------------------------

For attributes that have only a few possible values, you can add
another layer of indirection called a Lookup to confuse you... err,
normalize the data somewhat.  See :ref:`lookups` for more.

Other Fields
------------

A few more fields worth mentioning:

* ``allow_comments`` - whether users can comment on these NewsItems.
  You should also set has_newsitem_detail=True, because the detail
  page is where you would see comments and the comment form.

* ``allow_flagging`` - whether users can flag these NewsItems as
  inappropriate or spam. This leverages the ``ebpub.moderation``
  package.

* ``allow_charting`` - whether to show aggregate statistic charts on
  the detail page of this schema, such as number of recent items found
  in each Location, and number of recent items loaded per day.


Further Reading
---------------

For complete details on Schemas, you'll have to refer to the source
code in ``ebpub.db.models``.

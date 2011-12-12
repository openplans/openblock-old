=======
Widgets 
=======

Introduction 
============

OpenBlock's widgets allow you to integrate OpenBlock content in external sites and fully customize output using Django templates.

You can also do some advanced configuration to :ref:`"pin"
<pinned_items>` some news items so they don't expire from the widget
even if no longer current.

Widgets
======= 


Adding a new Widget
-------------------

A new widget can be created by visiting the OpenBlock admin site and selecting the `Add` link next to `Widgets` in the `Widgets` section.

.. TODO add a doc page about the admin UI and link to it from here

Configuring a Widget
--------------------

The configuration of a widget combines criteria for selecting items to
display with an output template for controlling the display of those items.

Currently items are always ordered by date.

==================== ============================================================
    Field			    Meaning
-------------------- ------------------------------------------------------------
   name               Human readable name of the widget.
-------------------- ------------------------------------------------------------
   slug               A unique identifier used to refer to the widget.
-------------------- ------------------------------------------------------------
   description        Notes on the use or meaning of the widget; not for public display.
-------------------- ------------------------------------------------------------
   template           Which output template to use to show the items (see below).
-------------------- ------------------------------------------------------------
   max items          Maximum number of items to show in the widget.
-------------------- ------------------------------------------------------------
   location           Restrict the output to a particular predefined location.
-------------------- ------------------------------------------------------------
   types              Restrict the output to only the selected
                      :doc:`Schema <schemas>` types.
                      If none are specified, any type is allowed.
-------------------- ------------------------------------------------------------
 item link template   If specified, links to item detail pages will use this 
                      template to determine where to link to.  
==================== ============================================================


Embedding Content
-----------------

The administrative page for each widget provides two ways you can embed the widget on an external site.

Javascript Based Inclusion
~~~~~~~~~~~~~~~~~~~~~~~~~~

To use javascript based inclusion, cut and paste the "Embed Code" for the widget into any web page.   The `div` will be replaced with the contents of the widget after the page loads.  The div and javascript may be placed anywhere and do not need to be kept together.

Server Side Inclusion
~~~~~~~~~~~~~~~~~~~~~

A request to the "Server Side Include URL" produces the output of the widget directly.
This URL is suitable for use with any CMS or web server that can stitch pages
together from content residing at different URLs or via sub-requests.



Templates
=========

Each widget must have a 'template' which is used to generate the
output that is included on the page.  These templates are normal
"Django Templates." You can read the official Django template docs at::

    http://docs.djangoproject.com/en/1.3/topics/templates/

There are also a variety of other tutorials and sources of information about Django templates available by casual googling. 

When the template is rendered, OpenBlock will supply a context consisting of the items that should be displayed in some manner in the widget along with some information about the widget's configuration.


Creating A Template
-------------------

A new template can be created by visiting the OpenBlock admin site and selecting the `Add` link next to `Templates` in the `Widgets` section.

Item Info
---------

The variable `items` contains a list of items that should be displayed by the widget.  This list is generally looped over using the `for` template tag, eg::

    {% for item in items %}
       <!-- output something about the item -->
       {{ item.title }}
    {% endfor %}

Each item in the list contains a basic set of fields, and may include several extension fields that are particular to the type (:doc:`schema <schemas>`) of the item.


Basic Fields
~~~~~~~~~~~~

==================== ============================================================
    Field			    Meaning
-------------------- ------------------------------------------------------------
  item.id             Openblock's unique identifier for this item.
-------------------- ------------------------------------------------------------
  item.title          The headline or title of the item.
-------------------- ------------------------------------------------------------
  item.internal_url   If the item is hosted by OpenBlock, this is a link to the
                      OpenBlock page about the item.  This value can be overridden
                      via the "Item Link Template" setting on a widget.
-------------------- ------------------------------------------------------------
  item.external_url   If the item is hosted by an outside site, this is a link to
                      the item.
-------------------- ------------------------------------------------------------
  item.pub_date       'Publication' date/time (the time when the content was added
                      to OpenBlock).  Must be formatted using a Django
                      date filter, eg ``{{item.pub_date|date:"Y m d h i"}}``.  See http://docs.djangoproject.com/en/1.3/ref/templates/builtins/#std:templatefilter-date
-------------------- ------------------------------------------------------------
  item.item_date     Date (without time) associated with item. Meaning varies by item type.
                     Must be formatted using a Django date filter, eg ``{{item.item_date|date:"Y m d"}}``.  See http://docs.djangoproject.com/en/1.3/ref/templates/builtins/#std:templatefilter-date
-------------------- ------------------------------------------------------------
  item.description    Description, body text, or text content of the item.
-------------------- ------------------------------------------------------------
  item.location.name  Text of location, address, place etc. Depending on item type 
                      and method of determining location, this may not be present or 
                      of varying meaning.
-------------------- ------------------------------------------------------------
  item.location.lat   Latitude of primary Point location of item.  
-------------------- ------------------------------------------------------------
  item.location.lon   Longitude of primary Point location of item.  
-------------------- -----------------------------------------------------------
  item.location.geom  The geometry object. See https://docs.djangoproject.com/en/dev/ref/contrib/gis/geos/#geometry-objects
-------------------- ------------------------------------------------------------
  item.schema.name    The name of the type of item, eg "Restaurant Inspection".
-------------------- ------------------------------------------------------------
  item.schema.slug    The unique identifier of the item's type.
-------------------- ------------------------------------------------------------
==================== ============================================================


Extension Fields
~~~~~~~~~~~~~~~~

Depending on the item's type (:doc:`schema <schemas>`), a number of extension fields may be present.  For example, a Restaurant Inspection might have a list of 'violations'; a Police Report might contain a field for a Crime Code.

Extended attributes can be accessed in two ways: By name via the ``attributes_by_name`` variable, or as an ordered list via the ``attributes`` variable.  The attributes list is ordered according to the Display Order configured in the :doc:`Schema's <schemas>` administrative user interface.

If you are using ``attributes_by_name``, you access each attribute according to its unique identifier as configured in the Schema, eg::

    {{ item.attributes_by_name.crime_code.value }}

If you are accessing the attributes as a list, you might say::

    {% for attribute in item.attributes %}
      {{ attribute.value }}
    {% endfor %}

No matter how it is accessed, each attribute houses the data and metadata about the attribute.  The following fields are available: 

==================== ============================================================
    Field			    Meaning
-------------------- ------------------------------------------------------------
  attribute.name       Unique identifier of the attribute.  This is the same as
                       the name used in attributes_by_name, eg "crime_code".
-------------------- ------------------------------------------------------------
  attribute.title      Human readable title of the attribute, eg "Crime Code".
-------------------- ------------------------------------------------------------
  attribute.is_list    True if the attribute's value is a list of values, eg
                       a list of codes or violations.
-------------------- ------------------------------------------------------------
  attribute.value      The value of the attribute.  This may be a list in
                       some cases, which can be tested via the is_list field.
==================== ============================================================


Widget Info
-----------

The context variable ``widget`` provides information about the widget. The ``widget`` variable has the following fields:

================== ============================================================
    Field			    Meaning
------------------ ------------------------------------------------------------
  widget.name      the human readable name of the widget
------------------ ------------------------------------------------------------
  widget.slug      a unique identifier for the widget
================== ============================================================


Item Link Templates
===================

An item link template can be specified to override the url used to link to 
detail pages for items listed in a widget by adjusting the 'item.internal_url' 
value available to the widget template.

For example, if your site has a different public url or url scheme than openblock uses internally, you can use this value to rewrite item links accordingly.

You may reference any of the fields shown above in your url template, but there is only one item, referenced as `item`.
URL templates follow the same django template syntax above, but should evaluate to 
a single url.  



Example::

    http://mypublicsite.com/xzy/openblock/items/{{item.id}}/
    
This will link items to mypublicsite and fill in the identifier for the item being 
linked to depending on the item.

**Note** unless you have a specific reason not to, use the urlencode filter on any value that may contain unsafe characters for urls.


Example:: 

    http://mypublicsite.com/track_click_and_redirect?realurl={{item.external_url|urlencode}}
    
Here, we link to a theoretical redirector on mypublicsite to capture a click through to an externally hosted (3rd party) detail page.

You are free to use django's full template syntax as long as the result contains a single url.  Here for example, we perform some logic to determine whether to link internally, or use the redirector based on the item's schema::

    {% if item.schema.slug == "restaurant-inspections" %}
        http://mypublicsite.com/xzy/openblock/inspections/{{item.id}}/
    {% else %}
        http://mypublicsite.com/track_click_and_redirect?realurl={{item.external_url|urlencode}}
    {% endif %}


.. _pinned_items:

Pinned Items, aka "Sticky Widgets"
==================================

Normally, a widget will show only the NewsItems that currently best
match the specified type(s) and location.  It's possible to configure
widgets to "pin" certain NewsItems so they stay visible -- or "stick"
-- either permanently, or until an expiration date you specify.

To do so, go to the admin UI and navigate to the widget you want to
change.  At top right, click the "configure sticky items" button.

The "Pinned Items" form shows a list of currently visible NewsItems on
the left column. To pin one, drag it into an empty slot on the right
column.

It will stay pinned in that position - either forever, or until the
optional Expiration Date (and optionally a time).

You can re-order the pinned items by dragging and dropping up and
down.

To manually remove a pinned item, just click the ``x`` button next to
it.

When done with your changes, click the Save button.


Intersecting Locations
=======================

There is a custom template tag you can use in your widget templates,
``get_locations_for_item``, which looks up any Locations that
intersect with an item and provides some basic info about each.
Usage looks like::

    {% get_locations_for_item newsitem location_type_slug (location_type_slug2 ...) as varname %}

The ``location_type_slug`` arguments will be used, in the order
given, to specify which types of locations to find.

The last argument is the name of the context variable in which to
put the result.

For each matching location, the result will contain a dictionary
with these keys: 'location_slug', 'location_name', 'location_type_slug',
'location_type_name'.

Here's an example template in which we build links for each
intersecting location::

     {% for item in news_items %}
       {% get_locations_for_item item 'village' 'town' 'city' as locations_info %}
       {% for loc_info in locations_info %}
         <li><a href="http://example.com/{{loc_info.location_slug}}/">
             Other News in {{ loc_info.location_name }}</a></li>
       {% endfor %}
     {% endfor %}

Example output might look like::

     <li><a href="http://example.com/villages/setauket/">
          Other News in Setauket</a></li>
     <li><a href="http://example.com/towns/brookhaven/">
          Other News in Brookhaven</a></li>

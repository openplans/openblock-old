=======
Widgets 
=======

Introduction 
============

Openblock's widgets allow you to integrate Openblock content in external sites and fully customize output using django templates. 


Widgets
======= 


Adding a new Widget
-------------------

A new widget can be created by visiting the openblock admin site and selecting the `Add` link next to `Widgets` in the `Widgets` section.

Configuring a Widget
--------------------

The configuration of a widget binds together criteria for selecting items and an output template. Currently items are always ordered by date.

==================== ============================================================
    Field			    Meaning
-------------------- ------------------------------------------------------------
   name               human readable name of the widget
-------------------- ------------------------------------------------------------
   slug               a unique identifier used to refer to the widget
-------------------- ------------------------------------------------------------
   description        internal notes on the use or meaning of the widget
-------------------- ------------------------------------------------------------
   template           which output template to use to show the items (see below)
-------------------- ------------------------------------------------------------
   max items          maximum number of items to show in the widget 
-------------------- ------------------------------------------------------------
   location           restrict the output to a particular predefined location
-------------------- ------------------------------------------------------------
   types              restrict the output to only the selected types.
                      If none are specified, any type is allowed. 
==================== ============================================================


Embedding Content
-----------------

The administrative page for each widget contains two sections that you can use on an external site to embed the widget. 

Javascript Based Inclusion
~~~~~~~~~~~~~~~~~~~~~~~~~~

To use javascript based inclusion, cut and paste the "Embed Code" for the widget into an external page.   The `div` will be replaced with the contents of the widget after the page loads.  The div and script may be placed anywhere and do not need to be kept together.

Server Side Inclusion
~~~~~~~~~~~~~~~~~~~~~

To use a server-side include, use the "Server Side Include URL." This URL produces the output of the widget directly and is suitable for CMS and web servers that can stitch pages together from content residing in different locations as a part of a request.


Templates
=========

Each widget must have a 'template' which is used to generate the output that is included on the page.  These templates are normal "Django Templates." You can read the official django docs at:: 

    http://docs.djangoproject.com/en/dev/topics/templates/

There are also a variety of other tutorials and sources of information about django templates available by casual googling. 

Openblock provides widget templates with a context consisting of the items that should be displayed in some manner in the widget along with some information about the widget's configuration. 


Creating A Template
-------------------

A new template can be created by visiting the openblock admin site and selecting the `Add` link next to `Templates` in the `Widgets` section.

Item Info
---------

The variable `items` contains a list of items that should be displayed by the widget.  This list is generally looped over using the `for` template tag, eg::

    {% for item in items %}
       <!-- output something about the item -->
       {{ item.title }}
    {% endfor %}

Each item in the list contains a basic set of fields, and may include several extension fields that are particular to the type of item.   


Basic Fields
~~~~~~~~~~~~

==================== ============================================================
    Field			    Meaning
-------------------- ------------------------------------------------------------
  item.title          the headline or title of the item 
-------------------- ------------------------------------------------------------
  item.internal_url   if the item is hosted by openblock, this is a link to the 
                      openblock page about the item.
-------------------- ------------------------------------------------------------
  item.external_url   if the item is hosted by an outside site, this is a link to 
                      the item.
-------------------- ------------------------------------------------------------
  item.pub_date       'publication' date/time must be formatted using a django 
                      date filter, eg {{item.pub_date|date:"Y m d h i"}}.  See http://docs.djangoproject.com/en/dev/ref/templates/builtins/#std:templatefilter-date
-------------------- ------------------------------------------------------------
item.item_date       Date associated with item (no time) Varying meaning by type. 
                     Must be formatted using a django date filter, eg {{item.item_date|date:"Y m d"}}.  See http://docs.djangoproject.com/en/dev/ref/templates/builtins/#std:templatefilter-date
-------------------- ------------------------------------------------------------
  item.description    description, body text or text content of the item 
-------------------- ------------------------------------------------------------
  item.location.name  Text of location, address, place etc. Depending on item type 
                      and method of determining location this may not be present or 
                      of varying meaning.
-------------------- ------------------------------------------------------------
  item.location.lat   Latitude of primary Point location of item.  
-------------------- ------------------------------------------------------------
  item.location.lon   Longitude of primary Point location of item.  
-------------------- ------------------------------------------------------------
item.schema.name      the name of the type of item, eg "Restaurant Inspection"
-------------------- ------------------------------------------------------------
item.schema.slug      the unique identifier of the item's type
==================== ============================================================


Extension Fields
~~~~~~~~~~~~~~~~

Depending on the type of item, a number of extension fields may be present.  For example a Restaurant Inspection has a list of 'violations', a Police Report might contain a field for a Crime Code.

Extended attributes can be navigated in two ways. 

By `name` via the `attributes_by_name` variable, or as an ordered list via the `attributes` variable.  The attributes list is ordered according to the Display Order configured in the administrative user interface.  

If you are using attributes_by_name, you access the attributes according to their unique identifier as configured in the item Schema, eg::

    {{ item.attributes_by_name.crime_code.value }}

If you are traversing the attributes a list, you might say:: 

    {% for attribute in item.attributes %}
      {{ attribute.value }}
    {% endfor %}

No matter how it is accessed, each attribute houses the data and metadata about the attribute.  The following fields are available: 

==================== ============================================================
    Field			    Meaning
-------------------- ------------------------------------------------------------
  attribute.name       unique identifier of the attribute.  This is the same as 
                       the name used in attributes_by_name, eg "crime_code"
-------------------- ------------------------------------------------------------
  attribute.title      human readable title of the attribute, eg "Crime Code"
-------------------- ------------------------------------------------------------
  attribute.is_list    true if the attribute's value is a list of values, eg 
                       a list of codes or violations.
-------------------- ------------------------------------------------------------
  attribute.value      the value of the attribute.  This may be a list in
                       some cases, which can be tested via the is_list field
==================== ============================================================


Widget Info
-----------

The widget info is available in the context via the variable `widget`.  The widget variable has the following fields

================== ============================================================
    Field			    Meaning
------------------ ------------------------------------------------------------
  widget.name      the human readable name of the widget
------------------ ------------------------------------------------------------
  widget.slug      a unique identifier for the widget
================== ============================================================

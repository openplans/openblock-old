=======
Widgets 
=======

Introduction 
============

Openblock's widgets allow you to integrate Openblock content in external sites and fully customize output using Django templates.


Widgets
======= 


Adding a new Widget
-------------------

A new widget can be created by visiting the openblock admin site and selecting the `Add` link next to `Widgets` in the `Widgets` section.

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
together from content residing at different URLs.


Templates
=========

Each widget must have a 'template' which is used to generate the
output that is included on the page.  These templates are normal
"Django Templates." You can read the official Django template docs at::

    http://docs.djangoproject.com/en/dev/topics/templates/

There are also a variety of other tutorials and sources of information about Django templates available by casual googling. 

When the template is rendered, Openblock will supply a context consisting of the items that should be displayed in some manner in the widget along with some information about the widget's configuration. 


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

Each item in the list contains a basic set of fields, and may include several extension fields that are particular to the type (:doc:`schema <schemas>`) of the item.


Basic Fields
~~~~~~~~~~~~

==================== ============================================================
    Field			    Meaning
-------------------- ------------------------------------------------------------
  item.title          The headline or title of the item.
-------------------- ------------------------------------------------------------
  item.internal_url   If the item is hosted by openblock, this is a link to the
                      openblock page about the item.
-------------------- ------------------------------------------------------------
  item.external_url   If the item is hosted by an outside site, this is a link to
                      the item.
-------------------- ------------------------------------------------------------
  item.pub_date       'Publication' date/time (the time when the content was added
                      to OpenBlock).  Must be formatted using a Django
                      date filter, eg ``{{item.pub_date|date:"Y m d h i"}}``.  See http://docs.djangoproject.com/en/dev/ref/templates/builtins/#std:templatefilter-date
-------------------- ------------------------------------------------------------
  item.item_date     Date (without time) associated with item. Meaning varies by item type.
                     Must be formatted using a Django date filter, eg ``{{item.item_date|date:"Y m d"}}``.  See http://docs.djangoproject.com/en/dev/ref/templates/builtins/#std:templatefilter-date
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
-------------------- ------------------------------------------------------------
  item.schema.name    The name of the type of item, eg "Restaurant Inspection".
-------------------- ------------------------------------------------------------
  item.schema.slug    The unique identifier of the item's type.
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

The context variable ``widget`` provides information about the widget. The ``widget`` variable has the following fields:

================== ============================================================
    Field			    Meaning
------------------ ------------------------------------------------------------
  widget.name      the human readable name of the widget
------------------ ------------------------------------------------------------
  widget.slug      a unique identifier for the widget
================== ============================================================

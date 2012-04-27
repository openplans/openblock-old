What Goes Where
~~~~~~~~~~~~~~~

OpenBlock needs to know how to store the data from each column of your
spreadsheet.

Each column might correspond to:

* a :ref:`core field of the NewsItem model <newsitem_core_fields>`.
  Only 'title' and some form of location are strictly required; the
  rest have reasonable defaults, but you typically want to provide
  'description' and 'item_date' and maybe 'url' too.  See below for
  more about how locations are recognized.

* Or, a :ref:`custom attribute <newsitem_attributes>` - if you have
  any - defined by the relevant :doc:`Schema <../main/schemas>`.

There are three ways you can tell OpenBlock where to store the data
from each cell of the spreadsheet.  Which one you choose depends on
what your spreadsheet looks like and how often you'll be loading
similar sheets:


1. Modify the original spreadsheet:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Modify or create your spreadsheet so the first row contains
NewsItem field names, and Attribute names relevant to your Schema.  Do
not provide a second spreadsheet. This is fine for a one-time deal;
Not recommended if you're going to be loading similar spreadsheets
frequently, because you'd have to modify the first row every time.

  .. list-table:: Example items sheet:
   :header-rows: 1

   * - title
     - item_date
     - description
     - location_name
     - reason
   * - Bob
     - 12/31/2011
     - group therapy
     - 123 Main St
     - feeling depressed
   * - Carol
     - 2012-01-01
     - film premiere
     - 456 Broadway
     - got free tickets

In this example, we assume the Schema has a text SchemaField named
"reason". If it doesn't, the fourth column would just be ignored.  All
the other columns correspond to core NewsItem fields.)


2. Spreadsheets with a header with column names:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Before the first time you want to load a spreadsheet, save a second
   copy of the spreadsheet.
2. In the copy, delete all rows but that first header row.
3. In the copy, in each cell of the *second* row, enter a NewsItem
   field name (or Attribute name relevant to your Schema).
4. In the second row, leave un-needed cells blank.
5. Use the copy as the second (optional) spreadsheet.

OpenBlock will use this second spreadsheet to "map" the original
column names to NewsItem fields and attributes. You can keep this
"mapping" spreadsheet handy for the next time you want to load a
similar spreadsheet.

  .. list-table:: Example items sheet:
   :header-rows: 1

   * - Who
     - When
     - What
     - Where
     - Why
   * - Bob
     - 12/31/2011
     - group therapy
     - 123 Main St
     - feeling depressed
   * - Carol
     - 2012-01-01
     - film premiere
     - 456 Broadway
     - got free tickets

  .. list-table:: Example mapping sheet:
   :header-rows: 1

   * - Who
     - When
     - What
     - Where
     - Why
   * - title
     - item_date
     - description
     - location_name
     - reason


3. Spreadsheets without a header:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Before the first time you want to load a spreadsheet, save a second
   copy of the spreadsheet.
2. In the copy, delete all rows but the first row.
3. In the copy, *replace* each cell in the first row with a NewsItem
   field name (or Attribute name relevant to your Schema).
4. In the first row, leave un-needed cells blank.
5. Provide the copy as the second (optional) spreadsheet.

In this case, OpenBlock will use this second spreadsheet to "map"
original column numbers to NewsItem fields and attributes. This
"mapping" spreadsheet can be re-used next time you load a similar
spreadsheet, too.

  .. list-table:: Example items sheet:
   :header-rows: 0

   * - Bob
     - 12/31/2011
     - group therapy
     - 123 Main St
     - feeling depressed
   * - Carol
     - 2012-01-01
     - film premiere
     - 456 Broadway
     - got free tickets

  .. list-table:: Example mapping sheet:
   :header-rows: 0

   * - title
     - item_date
     - description
     - location_name
     - reason


.. admonition:: What if some rows are inconsistent?

   OpenBlock will just ignore any rows that it can't successfully save.



Locations
~~~~~~~~~

OpenBlock will attempt to determine each NewsItem's
location according to this procedure:

* If there is a "location" field, try to split it into a
  latitude,longitude pair; if that's not within bounds, try treating
  it as a longitude,latitude pair. If it doesn't look like a pair of
  numbers, ignore it.
* If there are fields named "latitude" and "longitude", or "lat" and
  "lon" or "long" or "lng", use those.
* If there is a "location_name" field, try geocoding that.
* Otherwise, combine all text fields and try to extract addresses
  using :py:mod:`ebdata.nlp` and geocode them.
* If all of the above fails, just save the item with no location.
* If a point is found by any of the above means, but there is no
  "location_name", one will be derived by reverse-geocoding the point.

Avoiding Duplicates
~~~~~~~~~~~~~~~~~~~~

By default, OpenBlock assumes that any change in any field
except ``item_date`` or ``pub_date`` indicates a new, unique NewsItem.

This can result in duplicates if eg. a minor correction is made in a
description or title.  To avoid this, you would need to figure out
which fields really identify a unique row, and provide them
as the ``unique fields`` option.

(Note you can't currently use SchemaField names here; only core fields
of NewsItem.)

What Goes Where
~~~~~~~~~~~~~~~

The scraper needs to know how to map the cells of your spreadsheet
to fields of ``NewsItem`` (or attributes of the relevant
``Schema``).

There are three ways you can handle this:

* Modify or create your spreadsheet so the first row contains NewsItem
  field names (or Attribute names relevant to your Schema).
  Do not give a second argument to the script. This is
  fine for a one-time deal, or for manual uploads via the admin UI.
  Not recommended if you're going to be loading similar spreadsheets
  frequently.

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

  (In all these examples, we assume the Schema has a text field named
  "reason". If it doesn't, the fourth column would just be ignored.)

* -Or- if your spreadsheet's first row is a header with column names:

  1. Before the first time you want to run the scraper, save a second
     copy of the spreadsheet.
  2. In the copy, delete all rows but that first header row.
  3. In the copy, in each cell of the *second* row, enter a NewsItem
     field name (or Attribute name relevant to your Schema).
  4. In the second row, leave un-needed cells blank.
  5. Provide the copy as the second argument to the scraper.

  The scraper will use this second spreadsheet to "map" the original
  column names to NewsItem fields and attributes. This "mapping"
  spreadsheet can be re-used for future scraper runs, too.

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


* -Or- if your spreadsheet does not have a header with column names:

  1. Before the first time you want to run the scraper, save a second
     copy of the spreadsheet.
  2. In the copy, delete all rows but the first row.
  3. In the copy, *replace* each cell in the first row with a NewsItem
     field name (or Attribute name relevant to your Schema).
  4. In the first row, leave un-needed cells blank.
  5. Provide the copy as the second argument to the scraper.

  In this case, the scraper will use this second spreadsheet to "map"
  original column numbers to NewsItem fields and attributes. This
  "mapping" spreadsheet can be re-used for future scraper runs, too.

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

Avoiding Duplicates
~~~~~~~~~~~~~~~~~~~~

By default, the scraper assumes that any change in any field
except ``item_date`` or ``pub_date`` indicates a new NewsItem.

This can result in duplicates if eg. a minor correction is made in a
description or title.  To avoid this, you would need to figure out
what really is unique about each row. Then pass a comma-separated list
of NewsItem field names to the ``--unique-fields`` option.

(Note you can't currently use Attribute names here.)

Example:

.. code-block:: bash

  python ebdata/scrapers/general/spreadsheet/retrieval.py \
    --unique-fields=title,item_date \
    http://example.com/spreadsheet.csv


Locations
~~~~~~~~~

After figuring out which cells to use for which fields of the
NewsItem, the scraper will attempt to determine each NewsItem's
location according to this procedure:

* If there is a "location" field, try to split it into a
  latitude,longitude pair; if that's not within bounds, try treating
  it as a longitude,latitude pair.
* If there are fields named "latitude" and "longitude", or "lat" and
  "lon" or "long" or "lng", use those.
* If there is field we can use as "location_name", try geocoding that.
* Otherwise, combine all text fields and try to extract addresses
  using :py:mod:`ebdata.nlp` and geocode them.
* If all of the above fails, just save the item with no location.

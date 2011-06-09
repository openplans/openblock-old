=======================
Loading Geographic Data
=======================

Overview
========

OpenBlock needs several kinds of geographic data for your city or
region.  This document explains what you need and how to load it.

You will need the following:

 * Boundaries for local areas of interest to your users, such as
   neighborhoods, towns, ZIP codes, political districts, etc.

   It is recommended to set up ZIP codes first.

 * A database of city streets and blocks. This is used for geocoding,
   for address searches, and for browsing news by block.

   Note that this data is *not* used to generate background tile
   images for your maps.  Those are provided by a separate service
   such as Google Maps or a WMS server.  See :ref:`base_layer_configs`
   for more on setting up your map base layer.


Caveat: USA Only?
-----------------

OpenBlock was originally written with the assumption that it will be
installed in the USA, for a major metropolitan area.  It may be
possible to work around those assumptions, but using OpenBlock outside
the USA is not officially supported at this time.  We encourage
experimentation and asking questions on the mailing list; we know of
several people currently trying it in other countries.


ZIP Codes
=========

Finding ZIP Codes
-----------------

The US Census Bureau has shapefiles for all USA zip codes.  Go to
http://www2.census.gov/cgi-bin/shapefiles2009/national-files, select
your state from the drop-down, and submit. Toward the bottom of the
file list, you should see one labeled "5-Digit ZIP Code Tabulation
Area (2002)".

Download that file. It should have a name that looks like
``tl_2009_36_zcta5.zip`` where 36 is a state ID (in this case, 36 is
for New York).

Unzip the file. It should contain a number of files like this:

.. code-block:: bash

  $ unzip tl_2009_36_zcta5.zip 
  inflating: tl_2009_36_zcta5.dbf    
  inflating: tl_2009_36_zcta5.prj    
  inflating: tl_2009_36_zcta5.shp    
  inflating: tl_2009_36_zcta5.shp.xml  
  inflating: tl_2009_36_zcta5.shx


Loading ZIP Codes
------------------

The ZIP code file you downloaded is for an entire state. You're
probably not setting up OpenBlock for an entire state, so you'll need
to filter out those ZIP codes that are irrelevant to your area of
interest.  The zip import script allows you to do that, if you have
configured your :ref:`metro extent <metro_extent>`.

.. code-block:: bash

  $ ebpub/ebpub/db/bin/import_zips.py -v -b /path/to/where/you/unzipped/the/files/

The ``-b`` option tells it to filter out zip codes outside your
metro extent, and ``-v`` tells it to give verbose output.

If you need more filtering, you can also provide the "--city" option
to give a city name to filter against. Zip codes for other cities
would be skipped.

It will tell you which ZIP codes were skipped, and at the end, print a
count of how many were created.

Verifying ZIP Codes
-------------------

To verify that your ZIP codes loaded, point your browser at the home
page.  There should be a link to view "61 ZIP codes", or however many
you loaded. Follow that to see a list of them all, and click on one to
see a page about that ZIP code.

If you want to have a look "under the hood", you can use the django
admin UI to do so.  Browse to http://localhost:8000/admin , and enter
your admin username / password when prompted.

Navigate to "Db" -> "Location Types".  You should see that there is a
Location Type called "ZIP Code" in the system now.

Navigate back to "Db", then go to "Db" -> "Locations".  You should see
a number of ZIP codes in the list.  If you click on one, you should
see an edit form that contains a map, showing you the borders of this
ZIP code.

(TODO: screen shot?)

Streets / Blocks
================

Finding Blocks Data
-------------------

In the US, the Census Bureau's TIGER data website is again a good
source of data.
From http://www2.census.gov/cgi-bin/shapefiles2009/national-files,
you will need several files. First select the State you're interested
in.  Download the file labeled "Place (Current)".

Next, select the County you're interested in. From the county's page,
download the files labeled "All Lines", "Topological Faces (Polygons
With All Geocodes)", and "Feature Names Relationship File".

Unzip all these files.


Loading Blocks from US Census TIGER shapefiles
-----------------------------------------------

The block importer, like the zip importer, can filter out blocks
outside your named city. (It cannot yet filter based on metro extent.)

You can run it like this (assuming all the unzipped shapefiles are in
the current directory):

.. code-block:: bash

  $ ebpub/ebpub/streets/blockimport/tiger/import_blocks.py \
    --city=BOSTON tl_2009_25025_edges.shp tl_2009_25025_featnames.dbf tl_2009_25025_faces.dbf tl_2009_25_place.shp

The order of file arguments is important. First give the
edges.shp filename, then the featnames.dbf file, then the faces.dbf
file, then the place.shp file.

The filenames would be different from the example shown for a
different city/county, of course.

Be patient; it typically takes several minutes to run.


Loading Blocks from ESRI files
------------------------------

If you have access to proprietary ESRI blocks data, you can instead
use the script ``ebpub/streets/blockimport/esri/importers/blocks.py.``


Populating Streets and Intersections
------------------------------------

After all your blocks have loaded, you *must* run another script to
derive streets and intersections from the blocks data.
This typically takes several minutes for a large city.

The following commands must be run *once*, in exactly this order:

.. code-block:: bash

 $ ebpub/ebpub/streets/bin/populate_streets.py -v -v -v -v streets
 $ ebpub/ebpub/streets/bin/populate_streets.py -v -v -v -v block_intersections
 $ ebpub/ebpub/streets/bin/populate_streets.py -v -v -v -v intersections

The ``-v`` argument controls verbosity; give it fewer times for less output.

Verifying Blocks
----------------

Try starting up django and browsing or searching some blocks::

  $ django-admin.py runserver

Now browse http://localhost:8000/streets/ and have a look around.  You
should see a comprehensive list of streets on that page, and each
should link to a list of blocks.  On the list of blocks, each block
should link to a detail page that includes a map of a several-block
radius.

Other Locations: Neighborhoods, Etc.
====================================

What kinds of locations?
------------------------

Aside from ZIP codes, what kinds of geographic regions are you
interested in?

OpenBlock can handle any number of types of locations.  You can use
the admin UI to create as many location types as you want, by visiting
http://localhost:8000/admin/db/locationtype/ and click "Add".  Fill
out the fields as desired.  You'll want to enable both 'is_browsable'
and 'is_significant'.

Note also that the shapefile import scripts described below can create
LocationTypes for you automatically, so you may not need to do
anything in the admin UI.

You're limited only by the data you have available. Some suggestions:
try looking for neighborhoods/districts/wards, police precincts,
school districts, political districts...

Finding Location Data
---------------------

The trouble with loading local place data is that, at least in the
USA, there is no central agency responsible for all of it, and no
standards for how local governments should publish their geospatial
data. This means it's scattered all over the web, and we can't just
tell you where to find it.

Try googling for the name of your area plus "shapefiles".

Loading Location Data
----------------------

Once you have one or more Location Types defined, you can start
populating them.

Importing Locations From Shapefiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is a script that can import any kind of location from a
shapefile.  If a LocationType with the given slug doesn't exist, it will be
created when you run the script.

If you run it with the ``--help`` option, it will tell you how to use it::

 $ ./ebpub/ebpub/db/bin/import_locations.py  --help
 Usage: import_locations.py [options] type_slug /path/to/shapefile

 Options:
  -h, --help            show this help message and exit
  -n NAME_FIELD, --name-field=NAME_FIELD
                        field that contains location's name
  -i LAYER_ID, --layer-index=LAYER_ID
                        index of layer in shapefile
  -s SOURCE, --source=SOURCE
                        source metadata of the shapefile
  -v, --verbose         be verbose
  -b, --filter-bounds   exclude locations not within the lon/lat bounds of
                        your metro's extent (from your settings.py) (default
                        false)
  --type-name=TYPE_NAME
                        specifies the location type name
  --type-name-plural=TYPE_NAME_PLURAL
                        specifies the location type plural name


All of these are optional. The defaults often work fine, although
``--filter-bounds`` is usually a good idea, to exclude areas that
don't overlap with your metro extent.


Neighborhoods From Shapefiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is also a variant of the location importer just for
neighborhoods.  Historically, "neighborhoods" have been a bit special
to OpenBlock - there are some URLs hard-coded to expect that there
would be a LocationType with slug="neighborhoods".

Again, if you run this script with the ``--help`` option, it will tell you
how to use it::

 $ ./ebpub/ebpub/db/bin/import_hoods.py  --helpUsage: import_hoods.py [options] /path/to/shapefile

 Options:
  -h, --help            show this help message and exit
  -n NAME_FIELD, --name-field=NAME_FIELD
                        field that contains location's name
  -i LAYER_ID, --layer-index=LAYER_ID
                        index of layer in shapefile
  -s SOURCE, --source=SOURCE
                        source metadata of the shapefile
  -v, --verbose         be verbose
  -b, --filter-bounds   exclude locations not within the lon/lat bounds of
                        your metro's extent (from your settings.py) (default
                        false)


Again, all of the options are really optional. The defaults often work
fine, although ``--filter-bounds`` is usually a good idea, to exclude
areas that don't overlap with your metro extent.


Creating Locations By Hand
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Hand-drawing locations in the admin UI is possible too, but is only
recommended for areas that don't have to be very precise - it would be
too time-consuming, and there's no "undo" currently.

This might be appropriate for areas whose boundaries are informal.
For example, often local people will have a general sense of where
neighborhoods begin and end, but there may not be "official"
boundaries published anywhere.

To take this approach, just go in the admin UI to http://localhost:8000/admin/db/location/
and click "Add location".  Fill out the fields as desired. Then in the
map labeled "location", drag and zoom as desired, then click the "Draw
Polygons" control at upper right, and start adding points by
clicking.  Finish by double-clicking.   Afterward you can modify
points by clicking the "Modify" control, then dragging points as needed.

(TODO: screenshots?)

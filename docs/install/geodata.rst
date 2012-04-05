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

   It is recommended to set up ZIP codes first;
   if you are using a :ref:`multi_city` configuration, you should also
   load your city boundaries first.

 * A database of city streets and blocks. This is used for geocoding,
   for address searches, and for browsing news by block.

   Note that this data is *not* used to generate background tile
   images for your maps.  Those are provided by a separate service
   such as Google Maps or a WMS server.  See :ref:`base_layer_configs`
   for more on setting up your map base layer.



.. admonition:: Admin UI or command line?

  It is now possible to do all your geographic data loading via
  the OpenBlock's web admin UI at http://localhost:8000/admin,
  or via command-line scripts. It is purely a matter of preference.

.. admonition:: Multiple Cities?

  If the area you're interested in isn't a single city,
  be sure to read :ref:`metro_config`, especially the
  :ref:`multi_city` section.

.. admonition:: USA Only?

  OpenBlock was originally written with the assumption that it will be
  installed in the USA, for a major metropolitan area.  It may be
  possible to work around those assumptions, but using OpenBlock
  outside the USA is not officially supported at this time.  We
  encourage experimentation and asking questions on the mailing list;
  we know of several people currently trying it in other countries.


.. _background_tasks:

Background Tasks
-----------------

Several of the things you can do in the admin UI can potentially take
a long time, so they are launched as background tasks. If you want to
use these admin UI features, be sure to read this section.

You'll need to do this once at server start time:

.. code-block:: bash

    $ export DJANGO_SETTINGS_MODULE=myblock.settings  # change as needed
    $ django-admin.py process_tasks

Like the `runserver` command, this won't immediately exit. It will sit quietly
until there are background jobs to process for installing geographic data.

NB. If you are :doc:`installed on EC2 <aws>`, then ``django-admin.py
process_tasks`` is already run via a cron job.


.. admonition:: Why not Celery?

  We use `django-background-task
  <http://pypi.python.org/pypi/django-background-task>`_ for our
  background jobs.
  `Celery <http://celeryproject.org/>`_ is common in the Django world
  for handling asynchronous tasks, and is a more mature, robust, and featureful
  solution. However, our mandate was to make
  OpenBlock as easy as possible to install, and we could not justify
  burdening our users with yet another service to install, configure,
  and maintain.

.. _zipcodes:

US ZIP Codes
=============

Load ZIP Codes via Admin UI
----------------------------

If you have a list of the ZIP codes you'd like to install, just be sure the
:ref:`background task daemon <background_tasks>` is running. Then
you can surf to ``http://<your domain>/admin/db/location/`` and click the link "Import
ZIP Shapefiles".  You can pick your state, paste your list of ZIPs, and wait
for the import to finish.

You can do this several times if your area
crosses state lines.

When this is done,
skip down to :ref:`verifying_zipcodes` below.

(TODO: screen shot?)

Load ZIP Codes via Command Line
------------------------------------

Alternately, you can use command-line scripts to install ZIP codes.

The US Census Bureau has shapefiles for all USA zip codes.  
For the 2010 census files (now available for most parts of the USA),
go to http://www.census.gov/cgi-bin/geo/shapefiles2010/main , select
your state from the dropdown, and click "Download".

Unzip the resulting file. It should contain a number of files like this:

.. code-block:: bash

  $ unzip tl_2010_25_zcta510.zip 
  Archive:  tl_2010_25_zcta510.zip
  inflating: tl_2010_25_zcta510.dbf  
  inflating: tl_2010_25_zcta510.prj  
  inflating: tl_2010_25_zcta510.shp  
  inflating: tl_2010_25_zcta510.shp.xml  
  inflating: tl_2010_25_zcta510.shx  


The ZIP code file you downloaded is for an entire state. You're
probably not setting up OpenBlock for an entire state, so you'll need
to filter out those ZIP codes that are irrelevant to your area of
interest.  The zip import script allows you to do that, if you have
configured your :ref:`metro extent <metro_extent>`.

.. code-block:: bash

  $ import_zips_tiger -v -b /path/to/where/you/unzipped/the/files/

The ``-b`` option tells it to filter out zip codes outside your
metro extent, and ``-v`` tells it to give verbose output.

It will tell you which ZIP codes were skipped, and at the end, print a
count of how many were created.

.. _verifying_zipcodes:

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

.. _finding_blocks_data:

Finding Blocks Data
-------------------

In the US, the Census Bureau's TIGER data website is a good
source of data.
From http://www.census.gov/cgi-bin/geo/shapefiles2010/main,
you will need several files.

First, select "Places" from the dropdown on the main page.
On the next page, select your state, and download.

Next, go back to the
`main page <http://www.census.gov/cgi-bin/geo/shapefiles2010/main>`_,
select "All Lines" and submit. You'll then be prompted to select first your
state, and then your county.

Next, go to the `Relationship Files
<http://www.census.gov/cgi-bin/geo/shapefiles2010/layers.cgi>`_ page.
Under "Topological Faces (Polygons with all Geocodes)", select your
state, then select your county and download it.

Finally, go back to the `Relationship Files
<http://www.census.gov/cgi-bin/geo/shapefiles2010/layers.cgi>`_ page,
then under "Feature Names Relationship File", select your state and submit;
and on the next page, select your county and download it.

Loading Blocks using the Admin UI
----------------------------------------

It's easy to use the admin UI to load US Census shapefiles.
First, be sure the :ref:`background task daemon <background_tasks>` is
running.

Then you can surf to ``http://<your domain>/admin/streets/blocks/``
and click the link "Import Block Shapefiles".  Type in the city name
that these blocks are in, upload the four zip files you downloaded
above, click "Import", and wait for it to finish.

(It is likely to take several minutes - more or less, depending on
your hardware and the size of data; this is the most computationally intensive thing that
OpenBlock ever does.)

Streets, Intersections, and BlockIntersections will be done
automatically.

You can repeat this process if your area spans multiple shapefiles.
(It will get slower as the number of intersections grows.)

When done, skip down to :ref:`verifying_blocks`.

(TODO: screen shot?)


Loading Blocks using the Command Line
--------------------------------------------

You don't have to use the admin UI if you're happy at the command
line. It takes several steps.


Loading Blocks from Census TIGER files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, unzip all four files you downloaded in :ref:`finding_blocks_data`.

The block importer can filter out blocks outside the city named by the
``--city`` option. It can also filter out blocks outside your
:ref:`metro extent <metro_extent>` by passing the ``--filter-bounds``
option.

You can run it like this (assuming all the unzipped shapefiles are in
the current directory):

.. code-block:: bash

  $ import_blocks_tiger --city=BOSTON --filter-bounds \
    tl_2009_25025_edges.shp tl_2009_25025_featnames.dbf \
    tl_2009_25025_faces.dbf tl_2009_25_place.shp

The order of file arguments is important. First give the
edges.shp filename, then the featnames.dbf file, then the faces.dbf
file, then the place.shp file.

The filenames would be different from the example shown for a
different city/county, of course.

Be patient; it typically takes at least several minutes to run.

It can also filter out blocks outside of one or more locations by
passing the ``--filter-location`` option with a LocationType slug and
Location slug; for example:

.. code-block:: bash

  $ import_blocks_tiger --filter-location="cities:cambridge" \
    --filter-location="cities:newton" ...


If you run it with the ``--help`` option, it will tell you how about
all options:

.. code-block:: bash

 $ import_blocks_tiger  --help
 Usage: import_blocks_tiger edges.shp featnames.dbf faces.dbf place.shp
 
 Options:
  -h, --help            show this help message and exit
  -v, --verbose
  -c CITY, --city=CITY  A city name to filter against
  -f, --fix-cities      Whether to override "city" attribute of blocks and
                        streets by finding an intersecting Location of a city-
                        ish type. Only makes sense if you have configured
                        multiple_cities=True in the METRO_LIST of your
                        settings.py, and after you have created some
                        appropriate Locations.
  -b, --filter-bounds   Whether to skip blocks outside the metro extent from
                        your settings.py. Default True.
  -e ENCODING, --encoding=ENCODING
                        Encoding to use when reading the shapefile





Loading Blocks from ESRI files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have access to proprietary ESRI blocks data, you can instead
use the script ``ebpub/streets/blockimport/esri/importers/blocks.py.``


Populating Streets and Intersections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After all your blocks have loaded, you *must* run another script to
derive streets and intersections from the blocks data.
This typically takes several minutes for a large city.

The following commands must be run *once*, in exactly this order:

.. code-block:: bash

 $ populate_streets -v -v -v -v streets
 $ populate_streets -v -v -v -v block_intersections
 $ populate_streets -v -v -v -v intersections

The ``-v`` argument controls verbosity; give it fewer times for less output.

.. _verifying_blocks:

Verifying Blocks
----------------

Try starting up django and browsing or searching some blocks:

.. code-block:: bash

  $ django-admin.py runserver

Now browse http://localhost:8000/streets/ and have a look around.  You
should see a comprehensive list of streets on that page, and each
should link to a list of blocks.  On the list of blocks, each block
should link to a detail page that includes a map of a several-block
radius.

You should also be able to search. In the search bar at top right,
type in some addresses or intersections that you know should exist,
and verify that they're found.

.. admonition:: No Blocks?

  If you don't get any blocks, it's possible that the shapefiles you
  downloaded don't correspond to the geographic area you configured in
  settings.py.  Double-check that you downloaded the right file, and
  that your :ref:`metro extent <metro_extent>` covers the same area.

Other Locations: Neighborhoods, Etc.
====================================

.. _locationtype:

What kinds of locations?
------------------------

Aside from ZIP codes, what kinds of geographic regions are you
interested in?

OpenBlock can handle any number of types of locations.  You can use
the admin UI to create as many ``LocationTypes`` as you want, by visiting
http://localhost:8000/admin/db/locationtype/ and click "Add".  Fill
out the fields as desired.  You'll want to enable both 'is_browsable'
and 'is_significant'.

(Note also that the shapefile import scripts described below can create
LocationTypes for you automatically, so you may not need to do
anything in the admin UI.)

You're limited only by the data you have available. Some suggestions:
try looking for neighborhoods/districts/wards, police precincts,
school districts, political districts...

Drawing Locations by Hand
---------------------------

If you don't have shapefiles available, it's always possible to
hand-draw locations in the admin UI. This is a great option for
relatively simple shapes where you don't need to be very
precise with the edges.
This might also be appropriate for areas whose boundaries are informal.
For example, often local residents will have a general sense of where
neighborhoods begin and end, but there may not be "official"
boundaries published anywhere.

Just browse to `/admin/db/locations`, click "Add location", 
drag and zoom the map as desired, select a location
type, and start clicking away on the map.

When happy with your
polygon, double-click on the last point to stop drawing.

To modify it, click the "Modify features" icon in the map toolbar and then you
can click and drag individual points, or click a point and hit the
Delete key to remove a point.

There are Undo and Redo buttons, although the history will be
forgotten once you click the Save button on the form.

(TODO: screen shots?)

For precise complex shapes, it's just not practical to draw a
500-point polygon in our admin UI.


Finding Location Data
---------------------

The trouble with loading local place data is that, at least in the
USA, there is no central agency responsible for all of it, and no
standards for how local governments should publish their geospatial
data. This means it's scattered all over the web, and we can't just
tell you where to find it.

Try googling for the name of your area plus "shapefiles".


.. _loading_locations:

Loading Location Data
----------------------

Once you have one or more Location Types defined, you can start
populating them, either via the command line or the admin UI.

Admin UI: Importing Locations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Browse  to /admin/db/locations, click "Upload Shapefile",
and upload the zipped file you downloaded. Submit the form.

On the next screen, you can choose a Location Type,
then choose from the "layers" available in this shapefile (often there
is only one).

Then you get to choose which field contains the name of each location.
The form will show you an example value from each field, so it's
usually pretty obvious which field is the one to choose.
(If none of them make any sense, it's possible that this shapefile
isn't usable by OpenBlock.)

Submit the form and you're done.


.. _import_locations_from_shapefile:

Command Line: Importing Locations From Shapefiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is a script :py:mod:`import_locations <ebpub.db.bin.import_locations>` that can import any kind of location from a
shapefile.  If a LocationType with the given slug doesn't exist, it will be
created when you run the script.

If you run it with the ``--help`` option, it will tell you how to use it::

 $ import_locations  --help
 
 Usage: import_locations [options] type_slug /path/to/shapefile
 
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


Command Line: Neighborhoods From Shapefiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is also a variant of the location importer just for
neighborhoods.  Historically, "neighborhoods" have been a bit special
to OpenBlock - there are some URLs hard-coded to expect that there
would be a LocationType with slug="neighborhoods".

Again, if you run this script with the ``--help`` option, it will tell you
how to use it::

 $ import_neighborhoods  --help
 Usage: import_neighborhoods [options] /path/to/shapefile
 
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


.. _import_location_from_wkt:

Command Line: Add Location From WKT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is a script :py:mod:`add_location <ebpub.db.bin.add_location>`
that can create a single location given a `WKT <http://en.wikipedia.org/wiki/Well-known_text>`_ string.

If you run it with the ``--help`` option, it will tell you how to use it::

 $ import_locations  --help
 Usage: add_location.py [options] NAME WKT
 
 WKT is the geometry in "Well-Known Text" format.
 
 NAME is the human-readable name.
 The slug and normalized_name will be derived from it.
 
 Options:
  -h, --help            show this help message and exit
  -l LOC_TYPE_SLUG, --location_type=LOC_TYPE_SLUG
                        location type slug (default: neighborhoods)
  -s SOURCE, --source=SOURCE
                        source of data - name or URL of the place you found
                        it.


Can I load KML, GeoJSON, OpenStreetMap XML, or other kinds of files?
---------------------------------------------------------------------

No, at this time the only formats we can directly import are
shapefiles, and WKT.

Try using tools like `ogr2ogr <http://www.gdal.org/ogr2ogr.html>`_ to
convert your data into shapefiles.

.. _places:

Places
======

The ``Place`` model in ``ebpub.streets.models`` represents a generic
named landmark, such as "Millennium Park" or "Sears Tower".
A ``Place`` is just a Point with a name and an address, and optionally
a URL linking to some external page about this landmark.

``Places`` differ from the ``db.Location`` model in several ways.
First, ``Locations`` are relatively large areas described by polygons,
representing areas such as neighborhoods or postal codes.  OpenBlock
shows a list of Locations of each type, and it's expected that there
are relatively few of them - perhaps dozens. By contrast, a ``Place``
is just a single point and there could be many thousands of them.

``Places`` are entirely optional - you can run Openblock just fine
without using them.

The ``PlaceType`` model is used to categorize them, so you could have
a ``PlaceType`` named "Building", another one with named "Monument",
and so on.  You can also assign a map icon URL, a map color,

``Places``, can be used in several ways.

Places in the OpenBlock UI
----------------------------

As of OpenBlock 1.1, Places are shown in the "big map" view, which can
be found by clicking links labeled "Explore these items on a larger map"
from any view of NewsItems by schema.

.. (TODO: screenshot?)

If you click the blue "+" at top-right of that map, you can select
which PlaceTypes and Schemas are shown on the map.

As of OpenBlock version 1.1, Places aren't shown anywhere else in the
theme that comes with OpenBlock; this could of course change in future
releases.

Searching and Geocoding Places
-------------------------------

Place names can be used for geocoding, so if there exists a Place
named "Empire State Building", users can type that in the search bar;
the result will be a view of the block on which that Place exists.

Places in the REST API
----------------------

Places also can be accessed via the :doc:`../main/api` REST API, using the
:ref:`get_places` and :ref:`get_place_types` resources.


Alternate Names / Misspellings / Synonyms
=========================================

Often users will want to search your site for an address or location,
but they may spell it wrong - or it may have multiple names.
:doc:`Scraper scripts <../main/running_scrapers>` may encounter the
same problem.

OpenBlock provides a simple way that you can support these searches.

You can use the admin UI at ``/admin/streets/streetmisspelling/`` to
enter alternate street names. Click the "Add street misspelling"
button, then type in the correct and incorrect (or alternate) versions
of the street name.

Likewise, you can use the ``/admin/db/locationsynonym/`` page to add
alternate names for ``Locations``, and the ``/admin/db/placesynonym`` page
to add alternate names for :ref:`Places <places>`.

If you have a lot of misspellings to enter, you might consider putting
them in an XML, JSON, or YAML file and loading them as
`django fixtures. <https://docs.djangoproject.com/en/1.3/howto/initial-data/>`_

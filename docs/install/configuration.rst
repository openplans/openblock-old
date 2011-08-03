=====================
Configuring OpenBlock
=====================

You should have a look at ``ebpub/ebpub/settings_default.py``.  It
contains many comments about the purpose and possible values of the
various settings expected by OpenBlock.

A few items are worth special mention.

Sensitive Settings
==================

These are settings you *must* customize, and avoid putting in a
public place eg. a public version control system.

* ``PASSWORD_CREATE_SALT`` - this is used when users create a new account.
* ``PASSWORD_RESET_SALT`` - this is used when users reset their passwords.
* ``STAFF_COOKIE_VALUE`` - this is used for allowing staff members to see
  some parts of the site that other users cannot, such as :doc:`types
  of news items <../main/schemas>` that you're still working on.


.. _base_layer_configs:

Choosing Your Map Base Layer
============================

In your settings file, you have a couple of options for what you want
to use for your map base layer - the tiled images that give your map
street lines, geographic features, place names, etc.

Default: OpenStreetMap tiles hosted by OpenGeo
----------------------------------------------

This is the default setting in ``ebpub/ebpub/settings_default.py``.  It
is a fairly clean design inspired by everyblock.com, and was derived
from OpenStreetMap data.  It is free for use for any purpose, but note
that there have been some reliability issues with this server in the
past.

Other Publically Available Layers
---------------------------------

We support any base layer supported by `olwidget
<http://olwidget.org/olwidget/v0.4/doc/django-olwidget.html#general-map-display>`_.
More specifically:

Google Maps
~~~~~~~~~~~~


If your intended usage on your website meets Google's
`Terms of Service <http://code.google.com/apis/maps/faq.html#tos>`_, or
if you have a Premier account, you may be able to use Google Maps for
your base layer.

In your settings.py, set ``MAP_BASELAYER_TYPE`` to any of
'google.streets', 'google.physical', 'google.satellite', or 'google.hybrid'.
Then be sure to get an API key from Google and put it in your settings
file as ``GOOGLE_API_KEY``.


Open Street Map
~~~~~~~~~~~~~~~~~

Set ``MAP_BASELAYER_TYPE`` to either 'osm.mapnik' or 'osm.osmarender'.


Microsoft VirtualEarth / Bing Maps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set ``MAP_BASELAYER_TYPE`` to any of 've.road', 've.shaded',
've.aerial', or 've.hybrid'.

Yahoo Maps
~~~~~~~~~~~

Set ``MAP_BASELAYER_TYPE = 'yahoo'``
and be sure to set ``YAHOO_APP_ID`` to your Yahoo app id.


Other public WMS servers
~~~~~~~~~~~~~~~~~~~~~~~~

Set ``MAP_BASELAYER_TYPE`` to either 'wms.map' (not very useful for
OpenBlock) or 'wms.nasa'.

Blank (no base layer)
~~~~~~~~~~~~~~~~~~~~~~

Try ``MAP_BASELAYER_TYPE = 'wms.blank'``

CloudMade
~~~~~~~~~

Cloudmade hosts a *lot* of community-designed map base layers.
You can even design your own online using their tools.

Get an API key from them and put it in your settings as
``CLOUDMADE_API_KEY``.  Then set ``MAP_BASELAYER_TYPE = 'cloudmade.<num>'``
(where <num> is the number for a cloudmade style).
For example, 'cloudmade.998'.

To find interesting cloudmade style numbers, browse at
http://maps.cloudmade.com/editor ; the style number is at bottom right
of each style.


Custom or Other Base Layers
---------------------------

Do you have your own tile server running, or have a URL to something
else not in the above list? Great! You can use that with a few extra
settings.  This option takes a little more work; you will have to know
which `OpenLayers layer subclass
<http://dev.openlayers.org/docs/files/OpenLayers/Layer-js.html>`_ is
appropriate, and what parameters to pass to it.

In fact, this is how our default OpenGeo / OpenStreetMap layer is
configured, so let's use that as an example:

.. code-block:: python

 MAP_BASELAYER_TYPE = 'custom.opengeo_osm'
 
 MAP_CUSTOM_BASE_LAYERS = {
    'opengeo_osm':  # to use this, set MAP_BASELAYER_TYPE='custom.opengeo_osm'
        {"class": "WMS",  # The OpenLayers.Layer subclass to use.
         "args": [  # These are passed as arguments to the constructor.
            "OpenStreetMap (OpenGeo)",
            "http://maps.opengeo.org/geowebcache/service/wms",
            {"layers": "openstreetmap",
             "format": "image/png",
             "bgcolor": "#A1BDC4",
             },
            {"wrapDateLine": True
             },
            ],
         }
 }



Multiple databases?
===================

Note that while Django supports using multiple databases for different
model data, OpenBlock does not. This is because we use `South
<http://pypi.python.org/pypi/South>`_ to automate :ref:`database
migrations <migrations>`, and as of this writing South does not work
properly with a multi-database configuration.

.. _metro_config:

Configuring Cities / Towns: METRO_LIST
======================================

If you look at ``obdemo/obdemo/settings.py.in``, or at the
``settings.py`` that is generated when you start a :doc:`custom app
<custom>`, you will notice it contains a list named ``METRO_LIST``.

This list will (almost) always contain only one item, a dictionary
with configuration about your local region.

Most of the items in this dictionary are fairly self
explanatory. Here's an example for Boston:

.. code-block: python::
   METRO_LIST = [
    {
        # Extent of the metro, as a longitude/latitude bounding box.
        'extent': (-71.191153, 42.227865, -70.986487, 42.396978),

        # Whether this should be displayed to the public.
        'is_public': True,

        # Set this to True if the metro has multiple cities.
        'multiple_cities': False,

        # The major city in the metro.
        'city_name': 'Boston',

        # The SHORT_NAME in the settings file (also the subdomain).
        'short_name': SHORT_NAME,

        # The name of the metro, as opposed to the city (e.g., "Miami-Dade" instead of "Miami").
        'metro_name': 'Boston',

        # USPS abbreviation for the state.
        'state': 'MA',

        # Full name of state.
        'state_name': 'Massachusetts',

        # Time zone, as required by Django's TIME_ZONE setting.
        'time_zone': 'America/New_York',
    },
 ]


More information on a few of these follows.


short_name
----------

This is how OpenBlock knows which dictionary in METRO_LIST to use.
It must exactly match the value of settings.SHORT_NAME.

.. _metro_extent:

extent
------

This is a list of (leftmost longitude, lower latitude, rightmost
longitude, upper latitude).

One way to find these coordinates would be to use Google Maps to zoom
to your region, then point at the lower left corner of your area,
right-click, and select "Drop LatLng Marker".  You will see a marker
that displays the latitude,longitude of that point on the map. Then do
the same in the upper right corner.  

This defines a bounding box - the range of latitudes and longitudes
that are relevant to your area. It is used in many views as the
default bounding box when searching for relevant NewsItems.  It is
also used by some data-loading scripts to filter out data that's not
relevant to your area.

multiple_cities
---------------

Set 'multiple_cities' to True if you want OpenBlock to serve multiple
cities or towns. For example, you might be setting it up for a
county. In this example you could use the county name for 'city_name'
and 'metro_name'.  Or you might be somewhere like the San Francisco
Bay Area and wanting to include San Francisco, Oakland, Berkeley, and
so on.

Multi-city configuration has not been fully thought out yet; more
experimentation and documentation is needed. Please ask on the mailing
list.

When would you put more than one dictionary in METRO_LIST?
----------------------------------------------------------

The purpose of having more than one metro dictionary in ``METRO_LIST``
would be to run multiple OpenBlock sites for multiple metro areas with
some shared configuration.

To do this, you'd have one settings file containing the master
``METRO_LIST``, and then for each site you'd have its own settings
file that imports ``METRO_LIST`` (and any other shared stuff you like)
from the master file.  The site-specific settings file would also set
``settings.SHORT_NAME`` to match the ``'short_name'`` key of one of
the dictionaries.

Most people will probably not be doing that. This feature serves the
needs of `everyblock.com <http://everyblock.com>`_, which runs sites
for many cities.

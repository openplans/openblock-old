=====================
Configuring OpenBlock
=====================

You should have a look at ``ebpub/ebpub/settings_default.py``.  It
contains many comments about the purpose and possible values of the
various settings expected by OpenBlock.

A few items are worth special mention.

Sensitive Settings
==================

These are settings you need to customize, and avoid putting in a
public place eg. a public version control system.

* PASSWORD_CREATE_SALT - this is used when users create a new account.
* PASSWORD_RESET_SALT - this is used when users reset their passwords.
* STAFF_COOKIE_VALUE - this is used for allowing staff members to see
  some parts of the site that other users cannot, such as :doc:`types
  of news items <schemas>` that you're still working on.


.. _base_layer_configs:

Choosing Your Map Base Layer
============================

In your settings file, you have a couple of options for what you want
to use for your map base layer - the tiled images that give your map
street outlines, city names, etc.

Default: OpenStreetMap tiles hosted by OpenGeo
----------------------------------------------

This is the default setting in ``ebpub/ebpub/settings_default.py``.  It
is a fairly clean design inspired by everyblock.com, and was derived
from OpenStreetMap data.  It is free for use for any purpose, but note
that there have been some reliability issues with this server in the
past.

Any WMS Server
--------------

If you have access to any other
`Web Map Service <http://en.wikipedia.org/wiki/Web_Map_Service>`_
server that would be suitable for your site, you can use it by doing
this in your ``settings.py``::

  MAP_BASELAYER_TYPE='wms'
  WMS_URL="http://example.com/wms"  # insert the real URL here

Note we assume that the base layer uses
`spherical mercator projection <http://docs.openlayers.org/library/spherical_mercator.html>`_
(known variously as "EPSG:900913" or "PSG:3785").

Google Maps
-----------

If your intended usage on your website meets Google's
`Terms of Service <http://code.google.com/apis/maps/faq.html#tos>`_, or
if you have a Premier account, you may be able to use Google Maps for
your base layer.

You'll need this in your settings.py::

  MAP_BASELAYER_TYPE='google'
  GOOGLE_MAPS_KEY='your API key goes here'

Other base layers
-----------------

Patches welcome :)

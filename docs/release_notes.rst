OpenBlock 1.1.0 (TODO date here)
====================================

Upgrade Notes
-------------

New Features in 1.1
-------------------

* Email alerts can now be sent via a command-line script. (related to
  ticket #65). Includes docs for how to set it up with cron.

* Email alert signup can be disabled by removing 'ebpub.alerts' from
  settings.INSTALLED_APPS. (refs ticket #65).

* Flickr scraper (ticket #26).
  It's at ebdata/scrapers/general/flickr/flickr_retrieval.py
  and the associated schema can be loaded like so:
  ``django-admin.py loaddata ebdata/scrapers/general/flickr/photos_schema.json``

* Import locations from shapefiles in the admin UI (ticket #59).

* Import blocks from shapefiles in the admin UI.
  Also populates streets, blockintersections, and intersections.
  (ticket #215)

Bug fixes
---------

Nothing since 1.0.1.


Documentation
-------------

* Document email configuration.

Other
-----

Nothing since 1.0.1.




OpenBlock 1.0.1 (TODO date here)
================================

This was a minor bugfix (and docs) release, and was mostly identical to 1.0.0.

 * The georss scraper now gets coordinates in the right order on the
   first try, and populates location_name if it falls back to
   geocoding.

 * Fix date formatting on newsitem-detail page. (ticket #201)

 * The ``import_blocks_tiger`` and ``import_blocks_esri`` scripts had
   a circular import.

 * Fix a broken doctest in bootsrap.py.

Documentation
-------------

 * Added docs for cloning an EC2 instance from our Amazon AMI.

 * Remove nonexistent ``--city`` option from geodata docs.


Older Changes
==============

See :doc:`history`.

OpenBlock 1.0.1 (Sept 7, 2011)
====================================

This is a minor bugfix (and docs) release, and is mostly identical to 1.0.0.

Bug fixes
---------

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

 * Changed docs theme for easier navigation.


Older Changes
-------------

See :doc:`history`.

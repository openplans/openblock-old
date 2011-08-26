====================================
OpenBlock 1.1.0 (TODO date here)
====================================

Upgrade Notes
-------------

New Features in 1.1
-------------------

* Flickr scraper (ticket #26).
  It's at ebdata/scrapers/general/flickr/flickr_retrieval.py
  and the associated schema can be loaded like so:
  ``django-admin.py loaddata ebdata/scrapers/general/flickr/photos_schema.json``

* Import locations from shapefiles in the admin UI (ticket #59)

* Import blocks from shapefiles in the admin UI.
  Also populates streets, blockintersections, and intersections.
  (ticket #215)

Bug fixes
---------

* Return 404 instead of infinite loop if
  newsitem.schema.has_newsitem_detail is False but newsitem.url is
  empty. Closes #110

Documentation
-------------



Other
-----

* Removing lots of clustering code that's totally unused. (ticket #156)

Older Changes
==============

See :doc:`history`.

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

* Return 404 instead of infinite loop if
  newsitem.schema.has_newsitem_detail is False but newsitem.url is
  empty. Closes #110

 * The georss scraper now gets coordinates in the right order on the
   first try, and populates location_name if it falls back to
   geocoding.

Documentation
-------------

 * Added docs for cloning an EC2 instance from our Amazon AMI.

 * Added docs for email configuration. (ticket #205)

Other
-----

* Removing lots of clustering code that's totally unused. (ticket #156)

Older Changes
==============

See :doc:`history`.

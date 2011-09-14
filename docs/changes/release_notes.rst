OpenBlock 1.1.0 (TODO date here)
====================================

Upgrade Notes
-------------

New Features in 1.1
-------------------

* Support for future events, not just recent news.
  Several scrapers support this: the ma/boston/events scraper,
  and the general/meetups/ scraper.
  See docs in docs/packages/ebdata.rst.
  Ticket #246.

* Added a scraper for Meetup.com, in ebdata/scrapers/general/meetups.
  It's zero-configuration: it just loops over your zip codes and
  finds all meetups for those.

* Add a --reset option to ``update_aggregates`` script, deletes all
  aggregates and starts over. (ticket #221)

* Also add --verbose, --dry-run, and --help command-line options to
  ``update_aggregates``.

* Email alerts can now be sent via a command-line script. (related to
  ticket #65). Includes docs for how to set it up with cron.

* Email alert signup can be disabled by removing 'ebpub.alerts' from
  settings.INSTALLED_APPS. (refs ticket #65).

* Flickr scraper (ticket #26).
  It's at ebdata/scrapers/general/flickr/flickr_retrieval.py
  and the associated schema can be loaded like so:
  ``django-admin.py loaddata ebdata/scrapers/general/flickr/photos_schema.json``
  You'll need to set ``FLICKR_API_KEY`` and ``FLICKR_API_SECRET`` in
  settings.py.

* Import locations from shapefiles in the admin UI (ticket #59).

* Import blocks from shapefiles in the admin UI.
  Also populates streets, blockintersections, and intersections.
  (ticket #215)

Bug fixes
---------

* Georeport / open311 scraper: support unofficial 'page' parameter
  (ticket #245); also, use the 'address' field for location_name if
  provided.

* Seeclickfix scraper: allow city & state params, don't hardcode to
  boston; ticket #243.

* place_detail_overview wasn't actually filtering by place.

* ajax date charts would blow up if no results found.

* Fix ticket #77: Now filtering news by item_date instead of pub_date
  since that's the date that's shown and used for aggregates.

* Fix "show/hide" buttons on place detail page and account
  page. (tickets #204, #115)

* Fixed bug that caused many "Unknown" locations in location charts.
  (ticket #192). And removed "unknowns" entirely from the chart.

* Locations weren't capitalized on some pages. (ticket #202)

* GeoReport scraper: scrape a reasonable amount of days, not 60 every
  darn time

Documentation
-------------

* Document the out-of-the-box scrapers provided by ebdata.

* Document email configuration.

Other
-----

* Removed some unused template tags (SHORT_NAME, STATE_ABBREV, EB_SUBDOMAIN).

* Removed old version of map popups code.

OpenBlock 1.0.1 (Sept 7 2011)
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

 * Changed docs theme for easier navigation.


Older Changes
-------------

See :doc:`history`.

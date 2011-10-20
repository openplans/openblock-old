OpenBlock 1.1.0 (October 20, 2011)
=====================================

Upgrade Notes
-------------

* Due to an oversight, both obdemo and the generated custom
  applications prior to this release didn't include the TIME_ZONE setting.
  Please set settings.TIME_ZONE to an appropriate value.

* As usual, install all dependencies, eg if you are upgrading a source checkout::

   pip install -r ebpub/requirements.txt
   pip install -e ebpub
   pip install -r ebdata/requirements.txt
   pip install -e ebdata
   pip install -r obadmin/requirements.txt
   pip install -e obadmin
   pip install -r obdemo/requirements.txt
   pip install -e obdemo

* As usual, sync and migrate the database::

   django-admin.py syncdb
   django-admin.py migrate

Backward Incompatibilities
--------------------------

* ``updaterdaemon`` is now deprecated. It has not been removed,
  but we no longer recommend or support its use. Use cron or your favorite cron
  alternative instead for running scrapers regularly. See the
  "Running Scrapers" docs.  This allows us to close a bunch of tickets
  (#194, #51, #87, #180, #199, #222).

* removed redundant ``get_metro_bbox function``.

* remove unused template tags: SHORT_NAME, STATE_ABBREV, EB_SUBDOMAIN.

New Features in 1.1
-------------------

* Big shareable maps:
  "Explore these items on a larger map" link on all type-specific news lists.
  For example, http://demo.openblockproject.org/photos/filter/locations=neighborhoods,financial-district/
  links to http://bit.ly/njmZT6 which is shareable via permalink.
  (There is also undocumented support for embedding these via iframes.)

* Comments on NewsItems. Requires logging in,
  and the Schema must have allow_comments=True and has_detail=True.
  Needs docs.

* User-contributed "Neighbor Messages" and "Neighbor Events" news
  types, in the ebpub.neighbornews package.
  Needs docs.

* Better support for running in a multi-city area:

  - new get_city_locations() function to get a list of all Locations
    whose LocationType matches the 'city_location_type' from
    settings.METRO_LIST.

  - ``--fix-cities`` option to block import scripts (and admin UI)
    that allows fixing imported blocks so block.city matches an
    existing overlapping city-ish Location.

  - clean out intersections and streets on import, so they're
    regenerated safely.  Optionally skip regeneration.

  - some related URL bugfixes.

* Import Places from a CSV file via the admin UI.
  Needs docs.

* Date and time picker widgets on forms, where relevant. (#186)

* Block import supports filtering by your default metro extent, not
  just city name.  #160

* Support for future events, not just recent news.
  Several scrapers support this: the ma/boston/events scraper,
  and the general/meetups/ scraper, and the neighbornews package.
  See docs in docs/packages/ebdata.rst.
  (Ticket #246)

* Added a scraper for Meetup.com, in ebdata/scrapers/general/meetups.
  It's zero-configuration: it just loops over your zip codes and
  finds all meetups for those.
  It's at ebdata/scrapers/general/meetup/meetup_retrieval.py
  and the associated schema can be loaded like so:
  ``django-admin.py loaddata ebdata/scrapers/general/meetup/meetup_schema.json``
  You'll need to set ``MEETUP_API_KEY`` in settings.py.
  (Ticket #208)

* Add a --reset option to ``update_aggregates`` script, deletes all
  aggregates and starts over. (ticket #221)

* Add an ``ebpub/bin/delete_newsitems.py`` script, useful during schema
  development: wipes all newsitems and attributes and lookups of a
  given schema.

* Also add --quiet, --verbose, --dry-run, and --help command-line options to
  ``update_aggregates``.

* Email alerts can now be sent via a command-line script. (related to
  ticket #65). Includes docs for how to set it up with cron.

* Email alert signup can be disabled by removing 'ebpub.alerts' from
  settings.INSTALLED_APPS. (refs ticket #65).

* obdemo includes flickr and meetup in default news types.

* Flickr scraper (ticket #26).
  It's at ebdata/scrapers/general/flickr/flickr_retrieval.py
  and the associated schema can be loaded like so:
  ``django-admin.py loaddata ebdata/scrapers/general/flickr/photos_schema.json``
  You'll need to set ``FLICKR_API_KEY`` and ``FLICKR_API_SECRET`` in
  settings.py.

* Import locations from shapefiles in the admin UI (ticket #59).
  With documentation (ticket #234).

* Import blocks from shapefiles in the admin UI.
  Also populates streets, blockintersections, and intersections.
  (ticket #215)

* You can now set the default location type via
  settings.DEFAULT_LOCTYPE_SLUG.  (#148)

* Add --verbose and --quiet options to a bunch of command-line scripts
  and scrapers.

* Don't email scraper errors by default. That's just not nice, and
  cron already does that.

* All provided scrapers now log to settings.SCRAPER_LOGFILE_NAME.

* Custom apps generated via ``paster create -t openblock`` now include a
  wsgi file for use with mod_wsgi, an alternative settings file for
  use with django-admin process_tasks, a skeleton cron config,
  executable manage.sh and manage.py files. Also, manage.sh is now
  better at automatically finding and activating the virtualenv.

* obdemo also includes an example cron config file, a manage.sh file,
  and the alt. settings file. And no longer has an example
  updaterdaemon config.

* Our Amazon EC2 AMI will now use cron rather than updaterdaemon.
  Lots of other fixes in the EC2 scripts too.

Bugs fixed
----------

* Fixed broken map on feeds page, ticket #237.

* Added missing links to the password change form.

* CSRF protection everywhere, ticket #185.
  (As a side-effect we are now using JQuery 1.5.2.)

* Block import: generated names now sort numerically correctly
  (eg. "12-100 Main St" rather than "100-12 Main St")

* Block import: Don't try to guess right_from, right_to if not
  provided; that typically means there really is nothing on that
  side of the street.

* Boston demo: restaurant inspections scraper fixed to accomodate
  markup changes.

* De-hardcoded "neighborhoods" from various URLs. (#148)

* Zip code import UI has no default state (to avoid selecting Alabama
  by mistake).

* Zip code import now sets creation date (#233)

* Removed confusing NewsItem "About" page. (#228)

* Removed map from NewsItem list in admin UI, was too slow. (#219)

* SavedPlace now enforces that it has either a Block or a Location but
  not both. (#213)

* Items shown on map on schema filter page now use same filters as the
  items on the page. (#121)

* Support 2010 US Census tiger files (ticket #147). Use them for the
  Boston demo.

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
  page. (tickets #204, #115, 236)

* Fixed bug that caused many "Unknown" locations in location charts.
  (ticket #192). And removed "unknowns" entirely from the chart.

* Locations weren't capitalized on some pages. (ticket #202)

* Several bounds-related errors in Location import fixed (thanks to
  Bret Walker).

* Scrapers that create timezone-aware datetimes no longer blow up.

* GeoReport scraper: scrape a reasonable amount of days, not 60 every
  darn time. And do pagination (ticket #245)

* Georss scraper: Had the forwards / backwards coordinate test
  reversed :-\

* Georss scraper: Skip items with no location_name.

* Fix some migration ordering bugs.

* parse_date no longer blows up if you feed it a date or datetime instance.

* CSS fixes for ajax date charts on location overview page.

Documentation
-------------

* Lots more docs about loading geographic data.

* Document email configuration. (ticket #205)

* Document what you get when doing ``paster create -t openblock``.

* More docs about running on Amazon EC2.

* Describe differences from Everyblock

* More help_text added to several Model fields, so admin UI is
  slightly more self-documenting.

* Many many minor updates and tweaks.

Other
-----

* Upgraded to OpenLayers 2.11.  (ticket #250)

* Upgraded to Django 1.3.1.

* Upgraded to JQuery 1.5.2.

* Removed some unused template tags (SHORT_NAME, STATE_ABBREV, EB_SUBDOMAIN).

* Removed old version of map popups code.


Older Changes
-------------

See :doc:`history`.

OpenBlock 1.0.0 (August 30, 2011)
====================================

(This is largely unchanged from OpenBlock 1.0-beta1, so this is
just a repeat of the release notes from that version, modulo a few
small bug fixes.)

Upgrade Notes
-------------

* If you originally installed, or already upgraded to, OpenBlock 1.0
  Beta, you may skip the rest of this section.

* If you have an existing database that was built with 1.0a1 or
  earlier, you'll need to run this command to deal with the removal
  of the "django-apikey" dependency::

   django-admin.py migrate apikey 0001 --fake

* Many data-loading scripts that were scattered all over the source
  tree are now installed into your environment's ``bin``
  directory, so they should be on your ``$PATH``.
  Documentation has been updated accordingly.

* As usual, you should always run after upgrading::

   django-admin.py syncdb --migrate

  If you were unlucky and had last migrated with a git checkout
  including migrations that later got renamed or removed, you may get
  errors from migrating. In that case try adding the
  ``--delete-ghost-migrations`` option.

* Production webserver configurations will need a line added to get the
  django-olwidget javascript and CSS to show up.
  For example, for Apache you'd add a line like (adjust path as needed)::

    Alias /olwidget/ /home/openblock/openblock/src/django-olwidget/

* We now require Django 1.3. This probably doesn't have any impact on you.
  (ticket #155).

* Settings changes:

  - MAP_BASELAYER_TYPE can now be any base layer supported by
    olwidget, eg. "google.streets".  (Some require other settings for
    eg. API keys; see ebpub/settings_default.py for comments and
    examples.)

  - You can add custom base layers to your maps by creating
    the dictionary settings.MAP_CUSTOM_BASE_LAYERS.
    See ebpub/settings_default.py for an example.

    This replaces the WMS_URL setting from openblock 1.0a1 which is no
    longer supported.


New Features in 1.0 beta 1
--------------------------

 * ticket #33: Different map icons for different news item types.
   To use this, you can use the admin UI to configure "map icon url"
   or "map color" for a Schema.

 * ticket #85: Added ``streets.PlaceType`` model for categorizing ``Places``.
   These also can have individual colors or icon URLs on the /maps/
   view.  (Original ticket title was "'Landmark' location type")

 * ticket #142: JSON push API for news items.
   See docs/main/api.rst

 * ticket #187: REST API standard features: API key provisioning;
   require keys (or auth) for POST / DELETE; throttling

 * Import US Zip Codes as Locations, via the admin UI.

 * Work-in-progress: user-submitted content. See code in the
   ebpub/neighbornews app.

 * Work-in-progress: Maps you can share just by copy/pasting a URL.
   For a sneak preview, browse to /maps/.

 * Much better admin UI maps. (ticket #140: Bad admin UI for GeometryFields)

 * ticket #72: unify NewsItem.attributes and NewsItem.attribute_values

 * ticket #52: Proper validation for Street Misspellings in admin

 * ticket #157: fill in normalized name automatically

 * ticket #123: Configurable base layer should apply to admin UI maps
   too


Bug fixes
---------

This is not a complete list; not all bugs fixed in this release were
ticketed.

 * Fix #172: schema_detail view blows up (TypeError) if there are no
   NewsItems in the last 30 days, but there is a matching
   AggregateLocation. (That shouldn't happen, but evidently did with
   some boston demo schemas; also fixed a related possible off-by-one
   error that may have been a factor.)

 * Schema filter page: don't say 'You might want to try...' if there's
   nothing to try.

 * Fix bug where scrapers that create timezone-aware datetimes blow up

 * Fix errors in bounds checking in location importers, thanks to Bret
   Walker.

 * Fix missing import in Place admin

 * Fixed several bugs where django-nose (optional) would try to run
   some things that aren't tests.

 * ticket #110: Fix infinite loop if
   newsitem.schema.has_newsitem_detail is False but newsitem.url is
   empty; give 404 instead.

 * Importers should now not blow up if run more than once.

 * ticket #22: Scraper scripts in everyblock/cities/boston mostly
   don't work OOTB

 * ticket #79: Geotagging oddity

 * ticket #188: items.json doesn't include location_name

 * ticket #200: "obdemo bin scripts are documented, but don't get
   installed when installing obdemo non-editable"


Documentation
-------------

 * ticket #80: Documentation for Street Misspellings

 * ticket #162: Document pip / easy_install workarounds

 * ticket #139: Document adding database user / granting database
   access

 * ticket #198: version number in documentation

 * ticket #197: documentation for deploying static media

 * Fix outdated paths to example scrapers.

 * Fix location of get_or_create_lookup

 * Note differences from everyblock

Other
-----

 * ticket #181: Prepare packages for distribution on pypi.

 * ticket #83: Split out non-core packages into a separate download
   (``ebblog``, ``ebwiki``, ``ebgeo``, ``ebinternal``, and ``everyblock`` are now
   at https://github.com/openplans/openblock-extras )

 * ticket #156: Removing lots of clustering code that's totally unused.

 * remove a redundant get_metro_bbox function from
   ebpub.utils.geodjango;  use get_default_bounds(), does the same thing.

Older Changes
==============

See :doc:`history`.

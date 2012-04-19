OpenBlock 1.2.0 (UNRELEASED)
================================

Upgrade Notes
-------------

* As usual, install all dependencies, eg if you are upgrading a source checkout:

.. code-block:: bash

   pip install -r ebpub/requirements.txt
   pip install -e ebpub
   pip install -r ebdata/requirements.txt
   pip install -e ebdata
   pip install -r obadmin/requirements.txt
   pip install -e obadmin
   pip install -r obdemo/requirements.txt
   pip install -e obdemo

* As usual, sync and migrate the database:

.. code-block:: bash

   django-admin.py syncdb
   django-admin.py migrate


Backward Incompatibilities
--------------------------

* Removed mystery fields Schema.grab_bag, Schema.grab_bag_headline,
  Schema.intro. (Ticket #232)

* Removed safe_id_sort_reversed template tag; use the for loop's
  reverse option instead, eg.
  {% for item in itemlist|safe_id_sort reversed %}

* Moved the friendlydate template filter from ebpub.db.templatetags.eb
  into ebpub.db.templatetags.dateutils, where it seems to belong.

* Moved the recaptcha template tag from ebpub.neighbornews.templatetags into
  ebpub.db.templatetags.recaptcha_tags.
  Templates using it will now need to do {% load recaptcha_tags %}.

* Moved one obscure template tag, {% get_locations_for_item %},
  from ebpub.widgets.templatetags into ebpub.db.templatetags.recaptcha_tags.
  Templates using it will now need to do {% load eb %}.

* Renamed a bunch of template tag functions to match the name of the
  tag, eg. "do_filter_url()" is now "filter_url()".  This makes the
  API docs easier to read; it doesn't affect templates, only code that
  imports those functions directly - and there problably is none of
  that.

* Added a "View selected items on map" link and checkboxes on Schema
  filter pages, to allow viewing explicitly selected items on the "big map".

* Changed URLs used by the schema_filter view, so some bookmarks may
  break. (Ticket # 266)

* Removed unused ebpub/utils/mapmath.py module.

* Removed the EB_MEDIA_ROOT and EB_MEDIA_URL settings; now use
  django's normal MEDIA_ROOT and MEDIA_URL instead.

* Removed the ``ImproperCity`` exception, which only served to prevent
  using blocks in places such as unincorporated parts of counties,
  where there is nothing that could be called a 'city'.

* Removed unused NewsItem.block field, part of ticket #93.

* Removed ebdata/retrieval/scrapers/new_newsitem_list_detail.py,
  which wasn't used anywhere.

* Removed ebpub/streets/blockimport/tiger/import_blocks2010.py.
  Census 2010 files are now supported by the main import_blocks.py
  script.

* Removed item.intersecting from Widgets context; it was never
  documented properly. Instead use the new ``get_locations_for_item``
  template tag.

* Removed the old map javascript since we're now using
  openblockrichmap.js everywhere.


New Features in 1.2
-------------------

* Location import in admin UI now runs in background.

* Admin UI now provides links to view various things (NewsItems,
  Locations, Blocks, Streets, LocationTypes) on the live site.

* ``NewsItem`` now allows saving with an empty ``description.``;
  some things might really only have a title available.

* Support multiple types of Yahoo maps, due to olwidget upgrade.

* ebpub.geocoder.base.full_geocode() now has a convert_to_block
  argument, factored out from ebdata.retrieval.  If True, this
  tries to disambiguate bad blocks on good streets by rounding down
  to the nearest block, eg. converting '299 Wabash St' to '200 block
  of Wabash St.'  May help geocoding when eg. census data doesn't
  quite match reality.

* Schemas now have an ``edit_window`` field, representing how long (in
  hours) users are allowed to edit their content after it's created.  Used
  by the ``neighbornews`` forms.

* Rest API: Allow searching by multiple types (schemas).

* Added an admin UI for importing NewsItems from spreadsheets
  (currently only handles CSV and old-style Excel sheets; not .xslx)
  (Ticket #126)

* Added a generic spreadsheet scraper in
  ``ebdata/scrapers/general/spreadsheet/retrieval.py``,
  (currently only handles CSV and old-style Excel sheets; not .xslx)
  (Ticket #274)

* ``ebdata.scrapers.general.georss`` address-extraction fallback now
  looks in all tags that look like text.

* Search form now searches Places too.

* Neighbornews schemas now have chartable ``categories``.

* Allow overriding the template for schema_filter view on a per-schema
  basis, by creating a template named db/schema_filter/<schema>.html

* Nieghbornews schemas now have specific templates for the
  schema_filter view.

* Added ``featured`` flag on ``ebpub.db.Lookup`` model, allowing admins
  to designate some Lookup values as "special", for use in
  eg. navigation. (#268)

* Added a ``get_featured_lookups_by_schema`` template tag, puts into
  context a list of the "special" Lookup values for that schema. (#268)

* Added ``Lookup.objects.get_featured_lookup_for_item(newsitem, attribute_key)``
  method to find out which "featured" Lookups a newsitem has for a
  given attribute.

* Added a ``lookup_values_for_attribute`` template tag, dumps all
  values of a given db.attribute field as a JSON list.

* Made schema_filter the default view of Schemas, ticket # 272

* Added ``ebpub.moderation`` app that allows users to flag NewsItems
  as spam or inappropriate, and an admin UI for it;
  see :ref:`moderation` for more.

* Added ``Schema.allow_flagging`` boolean to toggle moderation
  flagging per schema. Allowed by default on the
  ``ebpub.neighbornews`` schemas.

* User-uploaded images now supported for NewsItems, and enabled for
  the ``ebpub.neighbornews`` user-contributed content schemas.

* Added new ``userlinks.html`` template so you can override the links
  at top right of the page.

* Added a ``get_locations_for_item`` template tag, see :doc:`../main/widgets`
  for more.

* Now works with Postgresql 9.1, ticket #262

* Nicer map controls thanks to Frank Hebbert, ticket #225

* Added advanced hook for filtering schemas based on arbitrary request
  data; implement this by assigning ``settings.SCHEMA_MANAGER_HOOK =
  'some_module:some_function'``, where ``some_module.some_function`` takes
  arguments (``request, manager``) and returns a ``models.Manager`` instance
  whose query sets will return the allowed Schemas.

* Add Vary headers to REST API responses, for more correct HTTP
  cache-ability.

* Auto-complete categories on the "neighbornews" add/edit forms.

* Optional ReCaptcha on the user-contributed ("Neighbornews") add/edit
  forms.

* User-contributed content ("neighbornews") now has edit and delete forms.

* Sensible defaults on most DateFields and DateTimeFields, can still
  be overridden.

* Logout now redirects you to whatever page you were viewing.

* Add a "properties" JSON field to the Profile model, for more
  flexible per-user metadata.

* User admin UI now shows Profiles and API keys inline.

* "Sticky widgets" aka "pinned" NewsItems in widgets: You can use the
  admin UI to make certain NewsItems stay visible in the widget
  permanently or until an expiration date that you set.

* settings.NEIGHBORNEWS_USE_CAPTCHA can now be a string path to a
  function.

* New NewsItem.objects.by_request() method for filtering based on
  eg. user privileges.

* New get_schema_manager(request) method for filtering based on
  current request, with an extensibility hook too.

* At least put the darn geocoder cache results in the admin so you can
  delete them manually if desired. Refs #163

* Admin UI option to save a copy of a schema as a new schema.


Bugs fixed
----------

* Location import (both command-line and admin UI) no longer blows up
  when re-importing the same Locations.

* RSS feed URLs fixed to use settings.EB_DOMAIN rather than the sites
  framework for getting the root URL.  For consistency with the rest
  of OpenBlock.

* parsing.normalize() and text.slugify() no longer blow up if fed
  non-string input.

* Schemas with allow_charting=False were shown on the schema_filter
  view, but not on its map. Fixed schema_filter_geojson so now they
  show up on map too.

* Fix filtering by location and date on big map page.

* Fix #281, wrong schemas shown on big map page.

* Map icon URLs for db.Location and streets.PlaceType can now be
  relative to STATIC_URL

* Fix #282, missing items on place detail pages

* Fix KeyError when an Attribute references a non-existent Lookup.

* Fix error on FilterChain.add(key, lookup) when key isn't a SchemaField.

* Should be possible to run OpenBlock at a URL prefix now; removed all
  hardcoded URLs. Ticket #90.

* Fix missing AJAX timeouts on "save place" button, thanks Tim Shedor.
  Ticket #269

* Fix error in NewsItem.objects.by_attribute() with many-to-many
  lookups: looking for [3,47] was finding any number starting with 3
  or ending with 47.

* Make ``manage.sh`` script executable.

* Fix rare error when we have a Block instance but its block range
  doesn't match the block range regex. Known example: 1600-7-1600-9
  Hanover Blvd. in Columbia, MO.

* Allow choosing multiple values when filtering via Lookups.
  Ticket # 267.

* Use query params instead of weird URIs for schema_filter view,
  ticket # 266.

* Remove bogus breadcrumbs from schema_filter page; ticket #270

* Filtering NewsItems by Block no longer causes 500 error.

* block_import_tiger can now be safely re-run on the same file,
  it won't create duplicate blocks anymore.

* Fixed double-logging of scrapers to the console.

* /streets/ list doesn't blow up if you haven't set
  DEFAULT_LOCTYPE_SLUG.

* Workaround for getting profile when request.user is a LazyUser
  instance.

* De-hardcoded more URLs.

* When using a too-old python version, our setup.py scripts now give a
  more informative error, instead of SyntaxError due to a `with`
  statement.

* Custom login view now works when going to admin site, and is
  compatible with (uses same cookies as) django.contrib.auth. Ticket
  #174

* Logout form was broken by bad template name. Fixed.

* Fix 500 error when user doesn't exist.

* Don't barf constructing richmaps url if there are no matching
  newsitems

* Group blocks by street on "choose a block" page, ticket # 263

* Store suffixes on streets with names like 'Wilson Park'; fixes some
  geocoding failures.


Documentation
-------------

* Auto-doc from all(?) ebpub, ebdata, obadmin, obdemo classes.
  Ticket #159.

* Document ``ebpub.db.bin`` scripts. Ticket #96.

* Documentation about comments and flagging of NewsItems. Ticket #252

* Better docs about template overrides, see :ref:`custom-look-feel`.

* Document ``ebpub.streets.Places``, see :ref:`places`.  Ticket #253

* Basic docs for ``ebpub.neighbornews``, see :ref:`user_content`.
  Ticket #211

* Document how to get the 2010 census files instead of 2009.

* Added docs on all the settings in settings_default.py.

* Better documentation about Schemas, SchemaFields, Attributes, and how they relate.

* Fixes to example crontab, thanks Tim Shedor

* Fix 500 error on newsitem.geojson, ticket #38


Other
-----

* Factored out the georss scraper's point-parsing code into a
  ``get_point()`` function in ebdata.retrieval.utils.

* Generic rss scraper is now the basis for
  ``obdemo.scrapers.add_news`` which did the same thing.

* Generic rss scraper is now a ListDetailScraper and
  RssListDetailScraper subclass. Ticket #242

* Upgrade jquery-ui to 1.8.17.

* Upgrade jquery to 1.7.1.

* Moved some NewsItemListDetailScraper functionality up into
  BaseScraper, so it's more widely usable.

* Deprecate log_exception(), the logging module actually does that
  already

* Move full_geocode() to ebpub.geocoder.base;  it was in an obscure place

* By default, one API key per user.  3 was kind of silly.



Older Changes
-------------

See :doc:`history`.

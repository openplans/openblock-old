OpenBlock 1.2.0 (UNRELEASED)
================================

Upgrade Notes
-------------

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

* Removed the EB_MEDIA_ROOT and EB_MEDIA_URL settings; now use
  django's normal MEDIA_ROOT and MEDIA_URL instead.

* Removed the ImproperCity exception, which only served to prevent
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


New Features in 1.2
-------------------

* User-uploaded images now supported for NewsItems, and enabled for
  the NeighborNews user-contributed content.

* Added new ``userlinks.html`` template so you can override the links
  at top right of the page.

* Added a ``get_locations_for_item`` template tag, see :doc:`widgets`
  for more.

* Added advanced hook for filtering schemas based on arbitrary request
  data; implement this by assigning ``settings.SCHEMA_MANAGER_HOOK =
  'some_module:some_function'``, where ``some_module.some_function`` takes
  arguments (``request, manager``) and returns a ``models.Manager`` instance
  whose query sets will return the allowed Schemas.

* Add Vary headers to REST API responses, for more correct HTTP
  cache-ability.

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


Bugs fixed
----------

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

Documentation
-------------

* Document how to get the 2010 census files instead of 2009.

* Added docs on all the settings in settings_default.py.

* Better documentation about Schemas, Attributes, and how they relate.

Other
-----

* Moved some NewsItemListDetailScraper functionality up into
  BaseScraper, so it's more widely usable.

Older Changes
-------------

See :doc:`history`.

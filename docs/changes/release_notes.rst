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

None.

New Features in 1.2
-------------------

* Logout now redirects you to whatever page you were viewing.

* Add a "properties" JSON field to the Profile model, for more
  flexible per-user metadata.

* User admin UI now shows Profiles and API keys inline.

* "Sticky widgets" aka "pinned" NewsItems in widgets: You can use the
  admin UI to make certain NewsItems stay visible in the widget
  permanently or until an expiration date that you set.


Bugs fixed
----------

* Workaround for getting profile when request.user is a LazyUser
  instance.

* When using a too-old python version, our setup.py scripts now give a
  more informative error, instead of SyntaxError due to a `with`
  statement.

* Custom login view now works when going to admin site. Ticket #174

* Logout form was broken by bad template name. Fixed.

Documentation
-------------

None.

Other
-----

None.


Older Changes
-------------

See :doc:`history`.

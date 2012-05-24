OpenBlock 1.3 (UNRELEASED)
===========================

.. _release-upgrade:

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


New Features in 1.3
-------------------

None.


Bugs fixed
----------

None.

Documentation
-------------

No changes.


Other
-----

No changes.


Older Changes
-------------

See :doc:`history`.

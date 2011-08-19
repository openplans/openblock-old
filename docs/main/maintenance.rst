=============================
Maintaining an OpenBlock Site
=============================

.. _migrations:

Upgrades
=========


Check the Release Notes
-----------------------


Database Migrations
-------------------

When upgrading your copy of the OpenBlock code, there may sometimes
be updates to Model code which require corresponding changes to your
existing database.

You can do this with one command (it's prudent to make a database
backup first):

.. code-block:: bash

    django-admin.py syncdb --migrate

To see what migrations exist and which ones you've already run,
you can do:

.. code-block:: bash

    django-admin.py migrate --list

Under the hood, this uses `South <http://pypi.python.org/pypi/South>`_
to automate these database migrations.  If you really want to see what
the migrations do, or need to write your own, you'll want to read the
`South documentation <http://south.aeracode.org/docs/>`_ to understand
how they work.  Then look in the ``migrations/`` subdirectories
located under the various app directories, notably
``ebpub/ebpub/db/migrations/`` to see what the existing migration
scripts look like.


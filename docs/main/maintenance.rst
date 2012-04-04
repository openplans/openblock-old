=============================
Maintaining an OpenBlock Site
=============================

.. _migrations:

Upgrades
=========


Make Backups!
-------------

As with any software, it is prudent to make backups of your database
and your code before attempting any upgrades, so that you can roll
back in the event of problems.

Check the Release Notes
-----------------------

See :doc:`../changes/release_notes` for a list of changes since the
last release.  It's probably more detailed than you need, but it's
good to know what you're getting, and this file will alert you of
backward incompatibilities that may impact any custom code you may
have written.

Update the Code
----------------

To install updated openblock code (from source) and all dependencies:

.. code-block:: bash

   pip install -r ebpub/requirements.txt
   pip install -e ebpub
   pip install -r ebdata/requirements.txt
   pip install -e ebdata
   pip install -r obadmin/requirements.txt
   pip install -e obadmin
   pip install -r obdemo/requirements.txt
   pip install -e obdemo

To upgrade from stable packages, the procedure is the same as
described at :ref:`stable_base_install`.

Database Migrations
-------------------

Whenever upgrading your copy of the OpenBlock code, there may
be updates to Model code which require corresponding changes to your
existing database.

You can do this with one command (it's prudent to make a database
backup first):

.. code-block:: bash

    django-admin.py syncdb --migrate

To check what migrations exist and which ones you've already run,
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

.. admonition::  If a migration gets stuck...

  If you run ``django-admin.py migrate`` and it seems to hang -- just
  sitting there indefinitely -- this typically means some other code is
  trying to write to the database, but the migration needs an exlusive
  lock to alter some tables, so it waits "forever" for those other
  scripts to go away. (See
  http://south.aeracode.org/wiki/FAQ#ImusingPostgreSQLandmigrationsjusthangindefinitely
  ). Typically these will be :doc:`scraper <running_scrapers>` scripts. To fix it, either
  restart the database, or ``kill`` all the other processes that are
  writing to the database. The migration should then finish with no trouble.


.. admonition:: Downtime

  When your code is installed but your database migrations haven't yet
  finished, the live site may give errors. It may make sense to
  temporarily replace your site with eg. a static "system is down for
  maintenance" page.  Doing so is beyond the scope of this
  documentation.

.. _moderation:

Moderating User-Submitted Content
=================================

If you have any Schemas with ``allow_flagging=True``, eg. if you have
:ref:`enabled the Neighbornews package <user_content>`
then logged-in users can flag those NewsItems as possible spam
or inappropriate content.

To moderate these flagged items, go to the admin UI and, under the
"Moderation" heading, click on "News Item Flags".

The list of flags is sorted with the most recent new, unmoderated flags
at top.

There are two ways you can moderate items: in bulk, or one at a time.

Moderating One at a Time
------------------------

If you click on a News Item Flag in the list, you'll see details about
the flagged News Item, who flagged it, when, and why.

There is also a link to the public view of the NewsItem, if you want to
examine it more fully in context.

You'll see two buttons at top: "Reject and Delete it" and "Approve it".
Click one of those and you're done.

Moderating in Bulk
-------------------

From the main list of News Item Flags, you can check all items you
want to approve or reject, and then from the "Action" pull-down menu,
you can select Approve, Reject, or Delete.

What effect does each action have?
----------------------------------

Whether singly or in bulk, here is the meaning of the actions you can
take:

* **Approve** - This will mark *all* flags on this NewsItem as
  "approved".  The flags are not deleted (though we might revisit that
  decision), but the NewsItem is no longer shown as flagged on the
  public site, and those Flags will be moved off the top of the list
  of new flags.

* **Delete** - This will **permanently** delete the NewsItem and all
  Flags on it.  You cannot undo this action.

* **Delete flag** - The selected Flag(s) is/are deleted. This has no
  effect on the associated NewsItem(s) and any Flags not specifically
  selected.

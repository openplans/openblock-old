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

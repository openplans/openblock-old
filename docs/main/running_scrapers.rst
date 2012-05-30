================
Running Scrapers
================

Once you've written your :doc:`scraper scripts <scraper_tutorial>`,
or chosen some :ref:`existing ones <ebdata-scrapers>`,
you'll need to re-run them frequently to keep the news on your site up
to date.

You can do this any way you like; :ref:`cron <cron>` would work fine.

.. _cron:

Cron Configuration
===================

Here's an example config file for running scrapers via
`cron <http://en.wikipedia.org/wiki/Cron>`__.

.. admonition:: important!

  You must set the ``DJANGO_SETTINGS_MODULE`` environment variable,
  and use the python interpreter that lives in your :ref:`virtualenv
  <virtualenv>`.  It's also crucial that the user who runs each
  cron job have permission to run those scripts, and permission to
  write to any log files, etc. that the scrapers write to.  I recommend
  using the same (non-root) user account you used for installing
  openblock.

::

  # Put this in a file in /etc/cron.d/
  SHELL=/bin/bash
  
  # Edit these as necessary
  DJANGO_SETTINGS_MODULE=obdemo.settings
  SCRAPERS=/path/to/ebdata/scrapers
  BINDIR=/path/to/virtualenv/bin
  PYTHON=/path/to/virtualenv/bin/python
  USER=openblock

  # Where do errors get emailed?
  MAILTO=somebody@example.com

  # Format:
  # m     h dom mon dow user   command

  # Retrieve flickr photos every 20 minutes.
  0,20,40 *  *   *  *   $USER  $PYTHON $SCRAPERS/general/flickr/flickr_retrieval.py -q
  
  # Meetup can be slow due to hitting rate limits.
  # Several times a day should be OK.
  0 7,18,22 * * * $PYTHON $SCRAPERS/general/meetup/meetup_retrieval.py -q
  
  # Aggregates every 6 min.
  */6     0  0   0  0   $USER  $BINDIR/update_aggregates --quiet


A more extensive example is in the ``obdemo`` source code; look for ``sample_crontab``.

As noted in :doc:`scraper_tutorial`, it's a very good idea if scripts have a
command-line option to discard all non-error output, since cron likes
to email you with all output. When using cron, silence is golden.

.. _updaterdaemon:

Updaterdaemon Configuration
===========================

.. admonition:: Deprecated!

  Since ``cron`` and similar tools work just fine,
  we deprecated UpdaterDaemon as of the 1.1 release.
  We are no longer maintaining or (as of 1.2) documenting it.

  If you really need to know how to use it, read the source.

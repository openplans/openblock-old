.. OpenBlock documentation master file, created by
   sphinx-quickstart on Mon Oct 25 10:49:32 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


=========
OpenBlock
=========

OpenBlock is a web application that allows users to browse and search
their local area for "hyper-local news" - to see what's going on
recently in the immediate geographic area.

.. _concept_overview:

Brief Overview: Concepts and Terminology
=========================================

OpenBlock is a *hyperlocal news platform*.  What we mean by that is
that, at its essence, OpenBlock is a web application (and web service)
that stores two kinds of information:

* *Local news*.  What's happening nearby?  This could be your original
  content, or :doc:`aggregated <main/scraper_tutorial>` from any
  number of sources on the web.

* *Local geographic data*.  What places do we care about?
  Neighborhoods, zip codes, school districts, police precincts?

OpenBlock allows you to explore that data in various ways: by
geographic area, small or large; by type of news; by various
categories relevant to the types of news you have; by text search; or
by any combination of the above.

News in OpenBlock is stored as *NewsItems*. In essence, a NewsItem is
just something that happened at one *time* and one *place*.  Each
NewsItem stores a timestamp, a geographic point, a title, a description,
and a few other generic fields.

Each NewsItem also has a type, which we call its *Schema*.  Schemas
are used to classify NewsItems and allow them to have extra
searchable, type-specific data.

For example: an OpenBlock site might provide both police reports and
restaurant inspections.  There would be one *Schema* representing
police reports, allowing each police report to store information about
what kinds of crime were committed.  There would be a second *Schema*
representing restaurant inspections, and it would allow each
inspection report to say whether the restaurant failed or passed, what
violations were observed, and so on.

A user is then able to browse *NewsItems* that are only police
reports, or only restaurant inspections, or both; or browse only
failed restaurant inspections; or browse crimes of a certain type, in
a certain location, during a certain time period; et cetera.

There is a `demo site <http://demo.openblockproject.org>`_ where you
can experiment with similar searches.

History
=======

OpenBlock began life as the open-source code released by
`Everyblock.com
<http://everyblock.com>`_ in June 2009.  Originally created by Adrian Holovaty
and the Everyblock team in 2007, it has been rebranded OpenBlock to avoid
trademark infringement, and is now developed as an open-source (GPL)
project at http://openblockproject.org.

Funding for both the 
`initial creation of Everyblock <http://www.newschallenge.org/winner/2007/everyblock>`_
and the `ongoing development of OpenBlock
<http://www.knightfoundation.org/news/press_room/knight_press_releases/detail.dot?id=364383>`_
was provided by the `Knight Foundation <http://www.knightfoundation.org/>`_.

Copyright / License
===================

OpenBlock code is licensed under the GNU General Public License
version 3.

A few modules were borrowed from other packages with other free
software licenses, e.g. "Modified BSD"-style licenses; these are
identified as such in the source code.

This documentation is licensed under the Creative Commons BY-SA 3.0
license.

For Developers
==============

This is a Django application, so it's highly recommended that you have
familiarity with the Django Web framework. The best places to learn
are the official `Django documentation <http://docs.djangoproject.com/>`_ and
the free `Django Book <http://www.djangobook.com/>`_.

Before you dive in, it's *highly* recommended you spend a little bit of
time browsing around http://demo.openblockproject.org and/or
http://EveryBlock.com to get a feel for what this software does.
(But note that the code has diverged considerably since 2009, so
everyblock.com has features not present in OpenBlock, and vice
versa; the visual design is quite different as well.)

Also, for a light conceptual background on some of this, particularly
the data storage aspect of :doc:`packages/ebpub`, watch the video "Behind the
scenes of EveryBlock.com" here: http://blip.tv/file/1957362


What's New in OpenBlock 1.2
============================

Highlights:

* Many tweaks to the public site, including: a more useful default
  view of a news type ("Schema"), nicer-looking map, add/edit/delete
  forms with autocomplete for user-contributed "neighbornews" content,

* Improved geocoding and better handling of some street names
  (eg. highways)

* Many administrative UI improvements

* Added a generic CSV scraper, and admin UI for loading CSV files by hand

* Administrative moderation of comments

* Lots of new hooks and template tags for people developing custom code

* :doc:`Python package API documentation <packages/index>`

* Over 30 bug fixes.

Full details are in the :doc:`Release Notes <changes/release_notes>`.

If upgrading be sure to read :ref:`release-upgrade`.
And if you've developed custom code, also read :ref:`backward-incompatibilities`.


.. include:: contents.rst

Indices and tables
==================


* :ref:`search`

.. * :ref:`genindex`
.. * :ref:`modindex`

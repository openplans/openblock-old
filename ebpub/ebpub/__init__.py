#   Copyright 2007,2008,2009,2011,2012 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Publishing system for block-specific news, as used by EveryBlock.com.

Before you dive in, it's *highly* recommend you spend a little bit of time
browsing around EveryBlock.com to get a feel for what this software does.

Also, for a light conceptual background on some of this, particularly the
data storage aspect, watch the video "Behind the scenes of EveryBlock.com"
here: http://blip.tv/file/1957362

Settings
========

ebpub requires a smorgasbord of eb-specific settings in your settings
file.  If you follow the :doc:`../install/custom` or :doc:`../install/demo_setup`
directions, they provide suitable settings files that you can
adjust as needed.  Otherwise, you might just start with the file
ebpub/settings.py and tweak that (or import from it in your own
settings file). The application won't work until you set the
following::

       DATABASES
       SHORT_NAME
       PASSWORD_CREATE_SALT
       PASSWORD_RESET_SALT
       METRO_LIST
       MEDIA_ROOT
       MEDIA_URL
       EB_DOMAIN
       DEFAULT_MAP_CENTER_LON
       DEFAULT_MAP_CENTER_LAT
       DEFAULT_MAP_ZOOM


Models
======

Broadly speaking, the system requires two different types of data:
geographic boundaries (Locations, Streets, Blocks and Intersections)
and news (Schemas and NewsItems).

For news-related models, see :py:mod:`ebpub.db.models`.

.. _geomodels:

For geographic models, see :py:mod:`ebpub.streets.models`,
and :py:class:`ebpub.db.models.Location`,
and also :doc:`../install/geodata`.


.. _custom-look-feel:

.. _email_alerts:

E-mail alerts
=============

Users can sign up for e-mail alerts via a form on the place_detail
pages. To send the e-mail alerts, just run the ``send_all()`` function
in ``ebpub/alerts/sending.py``.  You probably want to do this
regularly by :doc:`../main/running_scrapers`.

Accounts
========

OpenBlock uses a customized version of Django's User objects and
authentication infrastructure. ``ebpub.accounts`` comes with its own User
object and Django middleware that sets request.user to the User if
somebody's logged in.

See the package's docstrings for more detail.


FilterChains: Searching NewsItems, Making URLs for Searches
============================================================

Since searching NewsItems according to some schema, and building URLs
that represent those searches, are so important to OpenBlock, these
features have been encapsulated in the ``ebpub.db.schemafilters``
package.  It provides a ``FilterChain`` class, which you can treat as
an ordered collection of filters to apply to a NewsItem query.  Each
filter is represented by a subclass of ``NewsItemFilter`` and
represents filtering according to one criteria, eg. a date search, or
a search for some values of a ``SchemaField.``

Given a FilterChain, you can generate a URL to the ``schema_filter``
view with those parameters by calling ``filterchain.get_url()``.
There is also a ``{% filter_url %}`` template tag in
``ebpub.db.templatetags.eb_filter`` which you can use in templates.

See the ``schemafilter`` package's docstrings for more detail.  Most
of the views in ``ebpub.db.views`` make use of a FilterChain.


Template Tags
==============

``ebpub`` provides a number of custom tags for use in templates.  If
you are customizing templates, you will want to peruse the docstrings
of all the modules under ``ebpub.db.templatetags``.

"""

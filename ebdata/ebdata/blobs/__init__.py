#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

"""

.. _blobs:

blobs
=====

The blobs package is a Django app responsible for crawling, scraping,
extracting, and geocoding news articles from the web.

It is best suited for scraping "unstructured" websites that don't have
machine-readable feeds, eg. for scraping raw HTML and/or binary file
formats such as PDF or Excel.  (For sites that provide RSS or Atom
feeds, and/or an API, the :py:mod:`ebdata.retrieval` package may be more
suitable.)  (For dealing with binary file formats, you'll also want to
look into the :py:mod:`ebdata.parsing` package.)

Many examples can be found in the
`everyblock package <https://github.com/openplans/openblock-extras/tree/master/everyblock>`_.

The blobs app contains two models, ``Seed`` and ``Page``. ``Seed`` is a
news source, like the Chicago Tribune, and a ``Page`` is a particular html
page that was crawled from a Seed.

TODO: This really needs more explanation.
"""

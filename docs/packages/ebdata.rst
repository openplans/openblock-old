======
ebdata
======

Code to help write scripts that import/crawl/parse data from the web
into ebpub, as well as extract addresses from (English) text.

Scraper scripts will probably be built on either ebdata.retrieval_ or
ebdata.blobs_, depending on the type of content being scraped.

ebdata.blobs
============

The blobs package is a Django app responsible for crawling, scraping,
extracting, and geocoding news articles from the web.

It is best suited for scraping "unstructured" websites that don't have
machine-readable feeds, eg. for scraping raw HTML and/or binary file
formats such as PDF or Excel.  (For sites that provide RSS or Atom
feeds, and/or an API, the ebdata.retrieval_ package may be more
suitable.)  (For dealing with binary file formats, you'll also want to
look into the ebdata.parsing_ package.)

Many examples can be found in the everyblock_ package.

The blobs app contains two models, ``Seed`` and ``Page``. ``Seed`` is a
news source, like the Chicago Tribune, and a ``Page`` is a particular html
page that was crawled from a Seed.

TODO: This really needs more explanation.

ebdata.nlp
==========

The nlp package contains utilities for detecting locations in text. This
package is used by ebdata.blobs_, but if you want to use it directly, check out the
docstrings for the functions in ``ebdata.parsing.addresses.``


ebdata.parsing
==============

The parsing package contains helpers for reading different file types.

The ``dbf``, ``excel``, ``mdb``, and ``unicodecsv`` modules are for
reading stuctured data, and generally follow the python csv reader
api. See the code for more details on how to use them.

The pdf module is for converting pdf to text, and requires Xpdf.
http://www.foolabs.com/xpdf/download.html


ebdata.retrieval
================

The retrieval package contains a framework for writing scrapers for structured
data. Some examples can be found in
``ebdata/ebdata/scrapers/``.  There are more (unmaintained) examples of how to use this
framework in different situations in the everyblock_ package.

(For scraping data from unstructured sites, eg. sites that lack feeds
or machine-consumable API, it may be better to build on the
ebdata.blobs_ package.)

The most commonly used scraper base class is the
``NewsItemListDetailScraper``. It handles scraping list/detail types
of sites, and creating or updating NewsItem objects.  "List" could be
an RSS or Atom feed, or an HTML index, which links to "detail" pages;
these can be any format, such as HTML, XML, or JSON.  (In some cases,
the feed provides all the necessary information, and there's no need
to retrieve any detail pages.)

Generally, to run a scraper, you need to instantiate it, and then call its
``update()`` method. Sometimes the scraper will take arguments, but it varies on a
case-by-case basis; see the scrapers in ``ebdata/ebdata/scrapers`` for
examples. You can also run a scraper by calling its ``display_data()`` method. This
will run the scraper, but won't actually save any of the scraped data. It's
very useful for debugging, or when writing a scraper for the first time.

All of the methods and parameters you'll need to use are documented in
docstrings of ``ebdata.retrieval.scrapers.list_detail.ListDetailScraper`` and in
``ebdata.retrieval.scrapers.newsitem_list_detail.NewsItemListDetailScraper``.
``ListDetailScraper`` is a base class that handles
scraping, but doesn't actually have any methods for saving data.

The retrieval package also contains ``updaterdaemon``, which is a cron-like
facility for running scrapers. It comes with a unix-style init script, and its
configuration and examples are in ``ebdata/retrieval/updaterdaemon/config.py``.
More documentation at :doc:`../main/running_scrapers`.

.. _ebdata-scrapers:

ebdata.scrapers
===============

A collection of ready-to-run scraper scripts, with JSON fixture files
for loading the schemas needed by each scraper.

(If you want to write your own scrapers for other data sources, see
:doc:`../main/scraper_tutorial`.)

These generally leverage the tools in ebdata.retrieval.

All of them can be run as command-line scripts. Use the ``-h`` option to
see what options, if any, each script takes.

Flickr: ebdata.scrapers.general.flickr
---------------------------------------

Loads Flickr photos that are geotagged at a location within your
configured :ref:`metro extent <metro_extent>`.

You must set both ``settings.FLICKR_API_KEY`` and ``settings.FLICKR_API_SECRET``.

The scraper script is ``PATH/TO/ebdata/scrapers/general/flickr/flickr_retrieval.py``
and the schema can be loaded by doing
``django-admin.py loaddata PATH/TO/ebdata/scrapers/general/flickr/photos_schema.json``.


GeoRSS: ebdata.scrapers.general.georss
---------------------------------------

Loads any RSS or Atom feed.  It tries to extract a point location and
a location name from any feed according to the following strategy:

* First look for a GeoRSS point.
* If no point is found, look for a location name in
  standard GeoRSS or xCal elements; if found, geocode that.
* If no location name is found, try to find addresses
  in the title and/or description, and geocode that.
* If a point was found, but a location name was not,
  try to reverse-geocode the point.
* If all of the above fail, skip this item.

The scraper script is ``PATH/TO/ebdata/scrapers/general/georss/retrieval.py``
and a generic "local news" schema can be loaded by doing
``django-admin.py loaddata PATH/TO/ebdata/scrapers/general/georss/local_news_schema.json``.

Meetup: ebdata.scrapers.general.meetup
---------------------------------------

Retrieves upcoming Meetups from `meetup.com <http://meetup.com>`_.  USA-only.
This assumes you have loaded some :ref:`zipcodes`,
as it will attempt to load meetups for each zip code in turn.

You will need to get an API key, and set it as ``settings.MEETUP_API_KEY``.

This scraper may take hours to run, since Meetup's API has a rate
limit of 200 requests per hour (returning up to 200 meetups each), and
a large city may have thousands of meetups every day, and we're trying
to load all scheduled meetups for the next few months. The default
behavior is to run until the API's rate limit is hit, then wait till
the limit is lifted (typically 1 hour), and repeat until all pages for
all zip codes have been loaded.  If you'd rather do smaller batches,
try the ``--help`` option to see what options you have.

The scraper script is ``PATH/TO/ebdata/scrapers/general/meetup/meetup_retrieval.py``
and the schema can be loaded by doing
``django-admin.py loaddata PATH/TO/ebdata/scrapers/general/meetup/meetup_schema.json``.


Open311 / GeoReport: ebdata.scrapers.general.open311
------------------------------------------------------

A scraper for the
`Open311 / GeoReport API <http://wiki.open311.org/GeoReport_v2#GET_Service_Requests>`_
that is being adopted by a
`growing number of cities <http://wiki.open311.org/GeoReport_v2/Servers>`_
including many served by `SeeClickFix <http://seeclickfix.com>`.
(Tip: You can get an open311 endpoint for *any* location served by
seeclickfix, not just those listed on that page, by passing
``http://seeclickfix.com/<location-name>/open311/v2/``
as the API URL.)

It has many command-line options for passing API keys and so forth;
run it with the ``--help`` option.

The scraper script is ``PATH/TO/ebdata/scrapers/general/open311/georeportv2.py``
and a suitable schema can be loaded by doing
``django-admin.py loaddata PATH/TO/ebdata/scrapers/general/open311/open311_service_requests_schema.json``.


SeeClickFix: ebdata.scrapers.general.seeclickfix
-------------------------------------------------

A scraper for issues reported to `SeeClickFix <http://seeclickfix.com>`_.
Note you can also use the Open311 / GeoReport scraper described above,
since SeeClickFix supports the GeoReport API as well; we have both
scrapers because the SeeClickFix native API has been around longer.

Pass the city and state as command-line arguments.

The scraper script is ``PATH/TO/ebdata/scrapers/general/seeclickfix/seeclickfix_retrieval.py``
and a suitable schema can be loaded by doing
``django-admin.py loaddata PATH/TO/ebdata/scrapers/general/seeclickfix/seeclickfix_schema.json``.


ebdata.scrapers.us
------------------

Scrapers for specific city data sources in the USA. Currently this
includes only scrapers for Boston, MA:

* ebdata/scrapers/us/ma/boston/building_permits/
* ebdata/scrapers/us/ma/boston/businesses/
* ebdata/scrapers/us/ma/boston/events/
* ebdata/scrapers/us/ma/boston/police_reports/
* ebdata/scrapers/us/ma/boston/restaurants/

Many of these are used for http://demo.openblockproject.org.
For more information, see the source of each script.

ebdata.templatemaker
====================

The templatemaker package contains utilities for detecting the actual content
given a set of html pages that were generated from a template. For instance,
templatemaker helps detect and extract the actual article from a page that
could also contain navigation links, ads, etc.

This is used internally by ebdata.blobs_. It is not typically used
directly by scraper scripts.

ebdata.textmining
=================

The textmining package contains utilities for preprocessing html to strip out
things that templatemaker doesn't care about like comments, scripts, styles,
meta information, etc.  It is used by ebdata.templatemaker_ but may
also be used directly by scraper scripts.

.. _everyblock: https://github.com/openplans/openblock-extras/blob/master/docs/everyblock.rst

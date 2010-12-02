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

Many examples can be found in the :doc:`everyblock` package.

The blobs app contains two models, ``Seed`` and ``Page``. ``Seed`` is a
news source, like the Chicago Tribune, and a ``Page`` is a particular html
page that was crawled from a Seed.

TODO: This really needs more explanation.

ebdata.nlp
==========

The nlp package contains utilities for detecting locations in text. This
package is used by blobs, but if you want to use it directly, check out the
docstrings for the functions in ``ebdata.parsing.addresses.``


ebdata.parsing
==============

The parsing package contains helpers for reading different file types.

The ``dbf``, ``excel``, ``mdb``, and ``unicodecsv`` modules are for
reading stuctured data, and generally follow the python csv reader
api. See the code for more details on how to use the.

The pdf module is for converting pdf to text, and requires Xpdf.
http://www.foolabs.com/xpdf/download.html


ebdata.retrieval
================

The retrieval package contains a framework for writing scrapers for structured
data. There are many examples of how to use this framework in different
situation in the :doc:`everyblock` package.

(For scraping data from unstructured sites, eg. sites that lack feeds
or machine-consumable API, it may be better to build on the
ebdata.blobs_ package.)

The most commonly used scraper is the
``NewsItemListDetailScraper``. It handles scraping list/detail types
of sites, and creating or updating NewsItem objects.  "List" could be
an RSS or Atom feed, or an HTML index, which links to "detail" pages;
these can be any format, such as HTML, XML, or JSON.  (In some cases,
the feed provides all the necessary information, and there's no need
to retrieve any detail pages.)

Generally, to run a scraper, you need to instantiate it, and then call its
``update()`` method. Sometimes the scraper will take arguments, but it varies on a
case-by-case basis. You can read the scrapers in the :doc:`everyblock` package for
examples. You can also run a scraper by calling its `display_data()` method. This
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
More documentation at :doc:`../running_scrapers`.

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

=====================
Data Scraper Tutorial
=====================

Currently, anybody using OpenBlock will have to write their own
scraper scripts to import news data.

You have several options for how to write scraper scripts.
We'll look at each in turn:

1. :ref:`Use an Existing Scraper <ebdata-scrapers>` (separate page)
   if there is one that meets your needs.

2. :ref:`Use the OpenBlock REST API <scraping_rest_api>` to push data
   in from any script in any language that can make HTTP connections.

3. :ref:`Expediently hack a Python script <scraping_hack>` that creates instances of
   ebpub.db.NewsItem, in any way you like.

4. For ":ref:`list/detail <scraping_listdetail>`" sites, -- sites that display a list of records
   (eg. an RSS feed, or an HTML index page), with optional separate
   linked pages providing more detail about each record -- you can
   write a Python script that builds on the infrastructure in
   ``ebdata.retrieval.scrapers.newsitem_list_detail``.


5. For ":ref:`unstructured <scraping_blobs>`" sites - websites not intended for machine
   consumption, eg. big piles of HTML and/or binary files such as PDF
   or Excel - you can write a Python script that builds on ``ebdata.blobs``.


Let's look at each option in turn. But first, we need a Schema.


Setting up Schemas
==================

First of all, we're going to need a Schema that describes our
NewsItems.

This is fully documented at :doc:`schemas`.  Our examples will use
schemas that are bootstrapped by installing :doc:`../packages/obdemo`.


.. _scraping_rest_api:

Using the REST API
==================

This is an especially good solution if you mainly have experience with, or access to
programmers experienced with, languages other than Python.

You can use any programming language or tool that's able to make HTTP
connections to your OpenBlock site, and work with JSON data.
That's just about any modern language.

The general approach will be the same regardless of language:

* Fetch data from the source you're interested
* Parse the data
* For each news item you parsed:

  * Massage the item data into :ref:`the GeoJSON format <newsitem_json>` required by our API
  * Send a :ref:`POST request <post_items>` to push the news item into OpenBlock.

TODO: write an example, maybe in something other than Python?

.. _scraping_hack:

"Expedient Hack" scraping
=========================


If you only have a couple hours for a proof of concept, can write a
little Python, and aren't yet deeply familiar with OpenBlock, this is
a good way to start.

You can always refactor it into something more robust later.

The process is conceptually simple. The script should download some
data from the web, create one or more NewsItems whose fields are
populated with that data, and save the NewsItems.  The grunt work is
in extracting and massaging the data you need.

Here's an example. This script uses feedparser to fetch an RSS feed
from boston.com and creates a NewsItem for each entry:

.. code-block:: python

    #!/usr/bin/env python

    """A quick-hack news scraper script for Boston; consumes RSS feeds.
    """

    import datetime
    import feedparser
    import logging

    from django.contrib.gis.geos import Point
    from ebpub.db.models import NewsItem, Schema
    from ebpub.utils.logging import log_exception

    # Note there's an undocumented assumption in ebdata that we want to
    # unescape html before putting it in the db.
    from ebdata.retrieval.utils import convert_entities

    logger = logging.getLogger()

    def main():
        logger.info("Starting add_news")
        url = 'http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&subject=massachusetts&scope=bonzai'

        schema = Schema.objects.get(slug='local-news')

        for entry in feedparser.parse(url):
            try:
                # Check to see if we already have this one.
                item = NewsItem.objects.get(schema__id=schema.id, url=entry.link)
                logger.debug("Already have %r (id %d)" % (item.title, item.id))
            except NewsItem.DoesNotExist:
                # Nope, we need to create a new one.
                item = NewsItem()

            item.schema = schema
            item.title = convert_entities(entry.title)
            item.description = convert_entities(entry.description)
            item.url = entry.link
            item.item_date = datetime.datetime(*entry.updated_parsed[:6])
            item.pub_date = datetime.datetime(*entry.updated_parsed[:6])

            item.location_name = entry.get('x-calconnect-street') or entry.get('georss_featurename') or u''
            point = entry.get('georss_point') or entry.get('point')
            if not point:
                 # Don't bother saving. There's no point if there's no point ;)
                 continue
            x,y = point.split(' ')
            item.location = Point((float(y), float(x)))

            # If our Schema had some SchemaFields, we'd save them now like so:
            # item.attributes = {'foo': 'bar', ...}

            item.save()

        logger.info("Finished add_news")

    if __name__ == '__main__':
        import sys
        args = sys.argv
        loglevel = logging.INFO
        if '-q' in args:
            loglevel = logging.WARN
        logger.setLevel(loglevel)
        main()


This script actually runs.

So, what's left out? Among other things:

* We don't really do much error handling.

* This scraper doesn't demonstrate address parsing or geocoding, since
  this feed happens to provide location names and geographic points
  already.  If you need those features, you may want to look at how
  it's done in ``ebdata.retrieval.scrapers.base``.

* We get all our information directly from the feed and don't follow
  any links to other documents. Sometimes you need to do that.

* This schema doesn't require any custom attributes, so we don't show
  that. It's trivial though, just assign a dictionary to item.attributes.

Also notice the ``-q`` or ``--quiet`` command-line option that silences all non-error
output. This is an OpenBlock scraper convention intended to allow
running scrapers under :ref:`cron` without sending yourself tons of useless
email messages.

.. _scraping_listdetail:

Using NewsItemListDetailScraper for List/Detail pages
======================================================

A "list-detail site" is a site that displays a list of records (eg. an
RSS feed, or an HTML index page), which might be paginated. Each
record might have its own page -- a "detail" page -- or the list/feed
might include all the information you need.

Here's an example that doesn't use detail pages. This is a slightly
simplified version of the ``ebdata/scrapers/us/ma/boston/police_reports/retrieval.py``
script.  It uses a Schema that's loaded when bootstrapping the
``obdemo`` package.

Since this feed doesn't provide locations, we'll use ebdata's code for
address extraction and ebpub's geocoder:

.. code-block:: python

    from ebdata.nlp.addresses import parse_addresses
    from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
    from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
    from ebdata.textmining.treeutils import text_from_html
    from ebpub.db.models import NewsItem
    from ebpub.utils.logging import log_exception
    import logging
    import datetime


    class BPDNewsFeedScraper(RssListDetailScraper, NewsItemListDetailScraper):

        schema_slugs = ('police-reports',)
        has_detail = False

        def list_pages(self):
            # This gets called to iterate over pages containing lists of items.
            # We just have the one page.
            url = 'http://www.bpdnews.com/feed/'
            yield self.fetch_data(url)

        def existing_record(self, cleaned_record):
            # This gets called to see if we already have a matching NewsItem.
            url = cleaned_record['url']
            qs = NewsItem.objects.filter(schema__id=self.schema.id, url=url)
            try:
                return qs[0]
            except IndexError:
                return None

        def clean_list_record(self, record):
            if record['title'].startswith(u'Boston 24'):
                # We don't include the summary posts, those are citywide.
                self.logger.info("boston daily crime stats, we don't know how to "
                                 "handle these yet")
                raise SkipRecord

            date = datetime.date(*record['updated_parsed'][:3])

            # Get the precinct from the tags.
            precincts = ['A1', 'A7', 'B2', 'B3', 'C11', 'C6', 'D14', 'D4',
                         'E13', 'E18', 'E5']
            precinct = None
            tags = [t['term'] for t in record['tags']]
            if not tags:
                return

            for precinct in tags:
                if precinct in precincts:
                    # TODO: we need a LocationType for precincts, and shapes; and
                    # then we could set newsitem.location_object to the Location
                    # for this precinct.
                    break

            if not precinct:
                self.logger.debug("no precinct found in tags %r" % tags)

            description = record['summary']

            # This feed doesn't provide geographic data; we'll try to
            # extract addresses from the text, and stop on the first
            # one that successfully geocodes.
            # First we'll need some suitable text; throw away HTML tags.
            full_description = record['content'][0]['value']
            full_description = text_from_html(full_description)
            # This method on the RssListDetailScraper does the rest.
            location, location_name = self.get_point_and_location_name(
                record, address_text=full_description)

            if not (location or location_name):
                raise SkipRecord("No location or location_name")

            cleaned = dict(item_date=date,
                           location=location,
                           location_name=location_name,
                           title=record['title'],
                           description=description,
                           url=record['link'],
                           )
            return cleaned


        def save(self, old_record, list_record, detail_record):
            attributes = None
            # We don't use detail_record
            kwargs = list_record
            self.create_or_update(old_record, attributes, **kwargs)



    if __name__ == "__main__":
    import sys
    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    from optparse import OptionParser
    if argv is None:
        argv = sys.argv[1:]
    optparser = OptionParser()
    add_verbosity_options(optparser)
    scraper = BPDNewsFeedScraper()
    opts, args = optparser.parse_args(argv)
    setup_logging_from_opts(opts, scraper.logger)
    # During testing, do this instead:
    # scraper.display_data()
    scraper.update()


That's not too complex; three methods plus some command-line option
handling and you're done. Most of the
work was in save(), doing address parsing and geocoding. 

But you do have to understand how (and when) to implement those three
methods. It's highly recommended that you read the source code for
``ebdata.retrieval.scrapers.list_detail`` and ``ebdata.retrieval.scrapers.newsitem_list_detail``.

For a more complex example that does use detail pages and custom
attributes, see
``ebdata/scrapers/general/seeclickfix/seeclickfix_retrieval.py``.

What does this framework buy you? The advantage of using
ebdata.retrieval.scrapers.newsitem_list_detail for such sites is that
you get code and a framework for dealing with a lot of common cases:

* There's an ``RssListDetailScraper`` mix-in base class that handles both
  RSS and Atom feeds for the list page, with some support for
  pagination. (That saves us having to implement parse_list()).

* It supports all the advanced features of ebpub's NewsItems and
  Schemas, eg. arbitrary Attributes, Lookups, and the like (although
  this example doesn't use them).

* The ``create_newsitem()`` method can automatically geocode addresses if
  you have a single good address but no geographic location provided.

* The ``display_data()`` method allows you to test your feed
  without saving any data (or even without having a Schema created
  yet).  Call this instead of update() during testing.

* The ``safe_location()`` method (not shown) can verify that a location
  name (address) matches a provided latitude/longitude.

* The ``last_updated_time()`` method (not shown) keeps track of the last
  time you ran the scraper (very useful if your source data provides a
  way to limit the list to items newer than a date/time).

* There are hooks for cleaning up the data, see the various ``clean*``
  methods.

Disadvantage:

* It's fairly complex.

* You probably still have to do a fair amount of the error-handling,
  parsing (for things other than RSS or Atom feeds), and so forth.

* It requires you to understand the base classes
  (``NewsItemListDetailScraper`` and ``ListDetailScraper``), because it has a
  lot of "inversion of control" -- meaning, you use it by subclassing
  one or more of the base classes, and overriding various methods and
  attributes that get called by the base class as
  needed. Until you fully understand those base classes, this can be
  confusing.


For a more complete example that uses detail pages and some of those other
features, see ``ebdata/scrapers/general/seeclickfix/seeclickfix_retrieval.py``.

.. _scraping_blobs:

Blobs
=====

For "unstructured" sites, with a lot of raw HTML or binary files
(Excel, PDF, etc.), you may want to build something based on
ebdata.blobs.

We haven't done one of these yet.

Some examples you can peruse from the ``everyblock`` part of the
`the openblock-extras code <https://github.com/openplans/openblock-extras/tree/master/everyblock>`_
(note that we lack Schemas for any of these):

.. code-block:: text

  everyblock/cities/sf/zoning/new_retrieval.py
  everyblock/cities/boston/city_press_releases/retrieval.py
  everyblock/cities/seattle/city_press_releases/retrieval.py
  everyblock/cities/miami/city_press_releases/retrieval.py
  everyblock/cities/charlotte/city_council/retrieval.py
  everyblock/cities/charlotte/county_proceedings/retrieval.py
  everyblock/cities/chicago/city_press_releases/retrieval.py
  everyblock/cities/dc/news_articles/retrieval.py
  everyblock/cities/nyc/news_articles/retrieval.py
  everyblock/cities/philly/city_press_releases/retrieval.py
  everyblock/cities/philly/city_council/retrieval.py



Running Your Scrapers
=====================

Once you have scrapers written, you'll need to run them periodically.
Read :doc:`running_scrapers` for more.

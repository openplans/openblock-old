=====================
Data Scraper Tutorial
=====================

Currently, anybody using OpenBlock will have to write their own
scraper scripts to import data.

You have three options for how to write Python scraper scripts.
We'll look at each in turn:

1. :ref:`Expediently hack something <scraping_hack>` that creates instances of
   ebpub.db.NewsItem, in any way you like.

2. For ":ref:`list/detail <scraping_listdetail>`" sites, -- sites that display a list of records
   (eg. an RSS feed, or an HTML index page), with optional separate
   linked pages providing more detail about each record -- you can
   build on the infrastructure in
   ebdata.retrieval.scrapers.newsitem_list_detail.


3. For ":ref:`unstructured <scraping_blobs>`" sites - websites not intended for machine
   consumption, eg. big piles of HTML and/or binary files such as PDF
   or Excel - you can build on ebdata.blobs.

Let's look at each option in turn. But first, we need a Schema.


Setting up Schemas
==================

First of all, we're going to need a Schema that describes our
NewsItems.

This is fully documented at :doc:`schemas`.  Our examples will use
schemas that are bootstrapped by installing :doc:`packages/obdemo`.


.. _scraping_hack:

"Expedient Hack" scraping
=========================


If you only have a couple hours for a proof of concept, and aren't yet
deeply familiar with OpenBlock, this is a good way to start.

Sometimes you just want to quickly try an idea, and maybe you don't
know enough about OpenBlock to dive into its scraper infrastructure.
You can always refactor it into something more robust later.

The process is conceptually simple. The script should download some
data from the web, create one or more NewsItems whose fields are
populated with that data, and save the NewsItems.  The grunt work is
in extracting and massaging the data you need.

Here's an example. This script uses feedparser to fetch an RSS feed
from boston.com and creates a NewsItem for each entry::


    #!/usr/bin/env python

    """A quick-hack news scraper script for Boston; consumes RSS feeds.
    """

    import datetime
    import feedparser
    import logging

    from django.contrib.gis.geos import Point
    from ebpub.db.models import NewsItem, Schema
    from utils import log_exception

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
        main()


This script actually runs. A longer version is at ``obdemo/scrapers/add_news.py``.

So, what's left out? Among other things:

* We don't really do much error handling.

* This scraper doesn't demonstrate address parsing or geocoding, since
  this feed happens to provide location names and geographic points
  already.

* We get all our information directly from the feed and don't follow
  any links to other documents. Sometimes you need to do that.

* This schema doesn't require any custom attributes, so we don't show
  that. It's trivial though, just assign a dictionary to item.attributes.

.. _scraping_listdetail:

Using NewsItemListDetailScraper for List/Detail pages
======================================================

A "list-detail site" is a site that displays a list of records (eg. an
RSS feed, or an HTML index page), which might be paginated. Each
record might have its own page -- a "detail" page -- or the list/feed
might include all the information you need.

Here's an example that doesn't use detail pages. This is a slightly
simplified version of the ``obdemo/scrapers/bpdnews_retrieval.py``
script.  It uses a Schema that's loaded when bootstrapping obdemo.

Since this feed doesn't provide locations, we'll use ebdata's code for
address extraction and ebpub's geocoder::

    from ebdata.nlp.addresses import parse_addresses
    from ebdata.retrieval.scrapers.list_detail import RssListDetailScraper
    from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
    from ebdata.textmining.treeutils import text_from_html
    from ebpub.db.models import NewsItem
    from ebpub.geocoder import SmartGeocoder
    from ebpub.geocoder.base import GeocodingException
    from utils import log_exception
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

        def existing_record(self, record):
            # This gets called to see if we already have a matching NewsItem.
            url = record['link']
            qs = NewsItem.objects.filter(schema__id=self.schema.id, url=url)
            try:
                return qs[0]
            except IndexError:
                return None

        def save(self, old_record, list_record, detail_record):
            # This gets called once all parsing and cleanup is done.
            # It looks a lot like our 'expedient hack' code above.

            # We can ignore detail_record since has_detail is False.

            date = datetime.date(*list_record['updated_parsed'][:3])
            description = list_record['summary']

            # This feed doesn't provide geographic data; we'll try to
            # extract addresses from the text, and stop on the first
            # one that successfully geocodes.
            # First we'll need some suitable text; throw away HTML tags.
            full_description = list_record['content'][0]['value']
            full_description = text_from_html(full_description)
            addrs = parse_addresses(full_description)
            if not addrs:
                self.logger.info("no addresses found")
                return

            location = None
            location_name = u''
            block = None
            # Ready to geocode. If we had one location_name to try,
            # this could be done automatically in create_or_update(), but
            # we have multiple possible location_names.
            for addr, unused in addrs:
                addr = addr.strip()
                try:
                    location = SmartGeocoder().geocode(addr)
                except GeocodingException:
                    log_exception(level=logging.DEBUG)
                    continue
                location_name = location['address']
                block = location['block']
                location = location['point']
                break
            if location is None:
                self.logger.info("no addresses geocoded in %r" % list_record['title'])
                return

            kwargs = dict(item_date=date,
                          location=location,
                          location_name=location_name,
                          description=description,
                          title=list_record['title'],
                          url=list_record['link'],
                          )
            attributes = None
            self.create_or_update(old_record, attributes, **kwargs)


    if __name__ == "__main__":
        #from ebdata.retrieval import log_debug
        BPDNewsFeedScraper().update()
	# During testing, do this instead:
        # BPDNewsFeedScraper().display_data()

That's not too complex; three methods and you're done. Most of the
work was in save(), doing address parsing and geocoding. 

But you do have to understand how (and when) to implement those three
methods. It's highly recommended that you read
``ebdata.retrieval.scrapers.list_detail`` and ``ebdata.retrieval.scrapers.newsitem_list_detail``.

For a more complex example that does use detail pages and custom
attributes, see
``obdemo/scrapers/seeclickfix_retrieval.py``.

What does this framework buy you? The advantage of using
ebdata.retrieval.scrapers.newsitem_list_detail for such sites is that
you get code and a framework for dealing with a lot of common cases:

* There's an RssListDetailScraper mix-in base class that handles both
  RSS and Atom feeds for the list page, with some support for
  pagination. (That saves us having to implement parse_list()).

* It supports all the advanced features of ebpub's NewsItems and
  Schemas, eg. arbitrary Attributes, Lookups, and the like (although
  this example doesn't use them).

* The create_newsitem() method can automatically geocode addresses if
  you have a single good address but no geographic location provided.

* The display_data() method allows allows you to test your feed
  without saving any data (or even without having a Schema created
  yet).  Call this instead of update() during testing.

* The safe_location() method (not shown) can verify that a location
  name (address) matches a provided latitude/longitude.

* The last_updated_time() method (not shown) keeps track of the last
  time you ran the scraper (very useful if your source data provides a
  way to limit the list to items newer than a date/time).

* There are hooks for cleaning up the data, see the various clean*
  methods.

Disadvantage:

* It's fairly complex.

* You probably still have to do a fair amount of the error-handling,
  parsing (for things other than RSS or Atom feeds), and so forth.

* It requires you to understand the base classes
  (NewsItemListDetailScraper and ListDetailScraper), because it has a
  lot of inversion of control -- meaning, you use it by subclassing
  one or more of the base classes, and overriding various methods and
  attributes that get will get called by the base class as
  needed. Until you fully understand those base classes, this can be
  quite confusing.


For another example that uses detail pages and some of those other
features, see ``obdemo/scrapers/seeclickfix_retrieval.py``.

.. _scraping_blobs:

Blobs
=====

For "unstructured" sites, with a lot of raw HTML or binary files
(Excel, PDF, etc.), you may want to build something based on
ebdata.blobs.

We haven't done one of these yet.

Some examples you can peruse from the everyblock package (note that we
lack Schemas for any of these)::

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

==========================================
Creating a Custom Site Based on OpenBlock
==========================================

Things You Will Need
====================

To get anything useful out of your site, at minimum you will need the following:

 1. A database of streets in your city; for example
    TIGER/Line files from http://www.census.gov/geo/www/tiger/ .
    See :ref:`blocks`.

 2. Shapefiles with areas of interest - for example,
    neighborhoods, zip codes etc.
    See :ref:`locations`.

 3. Sources of news data to feed in.

    a. Configure the system with schemas for them.
       See the ebpub docs for :ref:`newsitem-schemas`.

    b. Write scraper scripts to retrieve news from your news sources and load
       it into the database. See :doc:`packages/ebdata`
       and http://developer.openblockproject.org/wiki/ScraperScripts .

 4. Optionally, customize the look and feel of the site.
    See the ebpub docs for :ref:`custom-look-feel`.

Gathering all this data and feeding it into the database can be a bit
of work at this point.  The ``obdemo/bin/bootstrap_demo.sh`` script
does all this for the demo site with Boston data, and should serve as
a decent example of how to do things in detail.

Setting up the app
==================

Begin by following :ref:`the steps to install the base software <baseinstall>`

    b. If they are not available as RSS feeds, you will need to write scraper scripts to retrieve your news sources and feed the data in. See :doc:`packages/ebdata` and http://developer.openblockproject.org/wiki/ScraperScripts

For more details, see :doc:`packages/ebpub`

For more documentation (in progress), see also:
    * http://developer.openblockproject.org/wiki/Data
    * http://developer.openblockproject.org/wiki/Ideal%20Feed%20Formats

The obdemo/bin/bootstrap_demo.sh script does all this for the demo
site.  You can dive into the other scripts that it calls to get more
details on how it all works.

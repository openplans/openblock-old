==========
obdemo
==========

This package contains code, templates, and configuration specific to
http://demo.openblockproject.org. 

They are intended to serve as a useful example of how to set up a site
based on the OpenBlock code.

By default, the site is set up to use Boston as the default location
for the maps.  You can change that by tweaking real_settings.py,
but then you're on your own for finding local data to load.

Prerequisites
=============

For system-specific lists of packages to install, see
http://developer.openblockproject.org/wiki/InstallationRequirements

Super-Quick Quickstart
======================

To get this demo up and running:

Run the script
 bin/bootstrap_demo.sh

and wait till it's done. If you get any errors, report them on the
ebcode google group.


Slightly Longer Quickstart
===========================

0. See the Prerequisites section above and make sure you have
everything installed.

1. You should have a 'bootstrap.py' script in the root of your
checkout. Run it.  This will install all the python software.

2. In obdemo/obdemo, copy the example config file
``real_settings.py.in`` to ``real_settings.py``

3. In ``real_settings.py``, uncomment and fill in all the settings.
   The application won't work until you set them.

   See the documentation/comments in that file, and/or refer to
   ebpub/settings.py for more info on what the various settings mean.

4. In the root of your checkout, run these commands to initialize
   your postgis database(s):

   bin/oblock setup_dbs
   bin/oblock sync_all


Starting the Test Server
========================

Run `obdemo/manage.py runserver` and go to http://127.0.0.1:8000/ in
your Web browser to see the site in action (with no data).


Loading Data
=============

OpenBlock is pretty boring without data!  You'll want to load some
geographic data and some local news.

If you used the obdemo/bin/bootstrap_demo.sh script, this is already
done :)

Otherwise, first you'll want to load Boston geographies. This will
take several minutes:

 obdemo/bin/import_boston_zips.sh
 obdemo/bin/import_boston_hoods.sh
 obdemo/bin/import_boston_blocks.sh

Then bootstrap some news item schema definitions:

 obdemo/bin/add_boston_news_schemas.sh


Then fetch some news from the web, this will take a few minutes:

 obdemo/bin/import_boston_news.sh


For testing random data you might also want to try
`obdemo/bin/random_news.py 100`
... where 100 is the number of random articles to generate.  You must
first have some locations in the database; it will assign randomly
generated local news articles to randomly chosen locations.


How The Demo Works
==================

obdemo uses the following parts of the OpenBlock codebase:

* ebpub does the heavy lifting.  We also use the base templates from
  here, although we override several of them.

* ebdata is used to feed news data into the system.

* everyblock provides some scraper scripts (which use ebdata).

For the maps, we use a free base layer based on Open Street Map and
hosted by OpenGeo.  Consequently, we don't need ebgeo or Mapnik.

We don't currently use ebblog, ebwiki, or ebinternal.


Deployment
==========

For production deployment it's not generally recommended to run
`manage.py runserver`.  Most people use apache and mod_wsgi.

There's a suitable wsgi script at obdemo/wsgi/obdemo.wsgi.  It
assumes that you installed openblock in a virtualenv whose root
directory is the same as the checkout root; that's how the
bootstrap.py script sets things up.  If that's not true, you can copy
and modify the script and adjust the env_root variable.  If you used
the bootstrap.py script, it should just work.

For more information on configuring Apache and running Django apps
under mod_wsgi, see
http://docs.djangoproject.com/en/1.1/howto/deployment/modwsgi/


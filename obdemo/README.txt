==========
obdemo
==========

This package contains code, templates, and configuration specific to
http://demo.openblockproject.org. 

They are intended to serve as a useful example of how to set up a site
based on the OpenBlock code.

By default, the site is set up to use Boston as the default location
for the maps.  You can change that by tweaking real_settings.py.

Quickstart
==========

To get this demo up and running:

0. Install PostgreSQL (8.3 or 8.4), PostGIS, Django (version 1.2),
psycopg2, and feedparser.

1. Create a PostGIS database, substituting the db name and user name
of your choice. For postgresql 8.3, do this::

  sudo -u postgres createuser -P <user name>
  createdb -T template1 <db name> -O <user name>
  createlang plpgsql <db name>
  psql -d <db name> -f /usr/share/postgresql-8.3-postgis/lwpostgis.sql
  psql -d <db name> -f /usr/share/postgresql-8.3-postgis/spatial_ref_sys.sql

Or for postgresql 8.4, do this::

  sudo -u postgres createuser -P <user name>
  createdb -T template1 <db name> -O <user name>
  createlang plpgsql <db name>
  psql -d <db name> -f /usr/share/postgresql/8.4/contrib/postgis.sql
  psql -d <db name> -f /usr/share/postgresql/8.4/contrib/spatial_ref_sys.sql


2. Install the obdemo package by putting it on your Python path. Also
   install the ebpub, ebdata, and obadmin packages.

   We recommend installing in a virtualenv.
   TODO: virtualenv documentation, links

   Each package has a setup.py script that you can run in the usual
   way, eg. for obdemo::

   python obdemo/setup.py develop

3. Copy the example config file ``real_settings.py.in`` to ``real_settings.py``

4. In ``real_settings.py``, uncomment and fill in all the settings.
   The application won't work until you set them.

   See the documentation/comments in that file, and/or refer to
   ebpub/settings.py for more info on what the various settings mean.

5. Run "obdemo/manage.py syncdb" to create all of the database tables.

6. Run "obdemo/manage.py runserver" and go to http://127.0.0.1:8000/ in your
   Web browser to see the site in action.



Loading Data
=============

Once you have the software running, it's time to get some data in.

Try the obdemo/bin/import_boston_blocks.sh script, which is based on
Don Kukral's documentation at
http://wiki.github.com/dkukral/everyblock/install-everyblock

For testing random data you might also want to try
"obdemo/bin/random_news.py 100"
... where 100 is the number of random articles to generate.  You must
first have some locations in the database; it will assign randomly
generated "local news" articles to randomly chosen locations.


How The Demo Works
==================

obdemo uses the following parts of the OpenBlock codebase:

* ebpub does the heavy lifting.

* ebdata is used to feed news data into the system.

* everyblock is used for templates, although we override some of them.

For the maps, we use a free base layer based on Open Street Map and
hosted by OpenGeo.  Consequently, we don't use ebgeo or Mapnik.

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


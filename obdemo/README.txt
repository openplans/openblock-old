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

TODO: document how best to get the dependencies, how to use
virtualenv, how to set up under mod_wsgi, etc.

0. Install PostgreSQL (8.3 or 8.4), PostGIS, Django (version 1.1.1),
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
   install the ebpub, ebdata, and ebgeo packages.

3. Copy the example config file ``real_settings.py.in`` to ``real_settings.py``

4. In ``real_settings.py``, uncomment and fill in all the settings.
   The application won't work until you set them.

   See the documentation/comments in ebpub/settings.py for more info
   on what the various settings mean.

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
generated "news" articles to randomly chosen locations.

====================
Installing OpenBlock
====================

These instructions cover manual installation of OpenBlock in a similar
configuration to `the OpenBlock demo site
<http://demo.openblockproject.org>`_.

Unlike the :doc:`demo_setup` instructions, there are more manual steps
and more prerequisites to install yourself.

.. _requirements:

If you have problems...
=======================

Please drop a line to the `ebcode google group <http://groups.google.com/group/ebcode>`_
or visit the openblock irc channel ``#openblock`` on freenode with any problems you encounter.  We're glad to help.

If you are having trouble with the installation of a particular package, you may want to try installing it by hand or seeing if your distribution offers a prebuilt package.  If you rerun the installation process, it should skip over anything you've done yourself.


System Requirements
===================

Linux, OSX, or some other Unix flavor.

Windows is not supported by the OpenBlock team, and may never be; but
patches are welcome :)

You also need:

* python 2.6  (2.7 might work; 2.5 is too old)
* Postgresql 8.3, 8.4, or 9.0
* PostGIS 1.4 or 1.5
* libxml2
* libxslt
* libgdal (and development libraries)
* git
* subversion
* `virtualenv <http://pypi.python.org/pypi/virtualenv>`_


For system-specific lists of packages to install, see
http://developer.openblockproject.org/wiki/InstallationRequirements
and let us know if your system isn't listed there!

Install the base software
============================

See the :ref:`requirements` above and make sure you have
everything installed.

Create a virtualenv that will contain the openblock software and all
its python dependencies::

    $ virtualenv openblock
    $ cd openblock
    $ source bin/activate

We'll be using ``pip`` to install some software, so make sure it's
installed (recent versions of virtualenv already do this, just making sure)::

    $ easy_install pip

Check out the openblock software::

    $ mkdir src/
    $ git clone git://github.com/openplans/openblock.git src/openblock


Install GDAL
------------

OpenBlock requires GDAL support. This isn't covered in detail
by the GeoDjango install docs.
*TODO: see if we can contribute this upstream?*

The easiest thing to do is check if your operating system already
provides a ready-made python GDAL package. For example, on Ubuntu,
this will work::

   $ sudo apt-get install python-gdal

If that works, you can skip to the next section.

Otherwise, it can be a little tricky, because you have to be careful
about which version you install, and in some cases it may not install
properly without a few extra arguments.

So, first, determine which version of the package you need. Try this
command::

   $ gdal-config --version

(If gdal-config isn't installed, go back and check that you've
installed all the requirements again; you need the GDAL development
libraries, on Ubuntu this is called ``libdal1-dev``.)

The output will be a version number like "1.6.3".
Your Python GDAL package version needs to match the first two digits.
So if ``gdal-config --version`` tells you "1.6.3", then you need
a version of Python GDAL that's less than 1.7.  This is important
because the easiest way to get a working version is to tell ``pip``
basically "get me the latest version that isn't too high."
Like this::

   $ pip install --no-install "GDAL<1.7"

Next, remove the bogus setup.cfg file ::

   $ rm -f build/GDAL/setup.cfg

Build the python package with some extra options, determined as
described below::

    $ python setup.py build_ext --gdal-config=gdal-config \
        --library-dirs=/usr/lib \
        --libraries=gdal1.6.0 \
        --include-dirs=/usr/include/gdal \
      install

The correct value for --library-dirs can be determined by running
``gdal-config --libs`` and looking for any output starting with
``-L``.  The correct value for --libraries can be determined with the
same command but looking for output beginning with ``-l``.  The
correct value for ``--include-dirs`` can be determined by running
``gdal-config --cflags`` and looking for output beginning with ``-I``.


Install all other Python packages
-------------------------------------

Pip can install the rest of our Python dependencies with a few
commands::

  $ pip install -r ebpub/requirements.txt -e ebpub
  $ pip install -r ebdata/requirements.txt -e ebdata
  $ pip install -r obdemo/requirements.txt -e obdemo


(We leave out :doc:`packages/ebgeo` because we assume you're not going to
be generating and serving your own map tiles.)


Database Installation
==================================

GeoDjango requires a spatial database.
Follow the `instructions here
<http://docs.djangoproject.com/en/1.2/ref/contrib/gis/install/#>`_,
being sure to use PostGIS as the spatial database.


OpenBlock is known to work with Postgresql 8.3, 8.4, or 9.0, and PostGIS
1.4 or 1.5.

.. _postgis_server:

PostGIS: On Another Server
--------------------------

If you're going to run postgresql on the same system where you're
installing openblock, skip ahead to :ref:`postgis_localhost`.

If you're going to run postgresql on a separate server, then --
assuming your database administrator can install postgis -- you'll
only need the postgresql client packages.  On Ubuntu, for example, you
can run ``sudo apt-get install postgresql-client``.

You'll have to work out any connection or authentication details with
your database administrator.

.. _postgis_localhost:

PostGIS: On Localhost
---------------------

Installing Postgresql and PostGIS depends on your
platform; but
http://developer.openblockproject.org/wiki/InstallationRequirements
may list the package names needed on your system,
and `GeoDjango's platform-specific instructions
<http://docs.djangoproject.com/en/1.2/ref/contrib/gis/install/#platform-specific-instructions>`_
may have some information for you as well.

You'll also need to make sure that the ``openblock`` user can connect
to the postgresql database.  The
easiest way to allow this is to find the ``pg_hba.conf`` file
under ``etc`` (the precise location varies, but for postgresql
8.4 on Ubuntu it's ``/etc/postgresql/8.4/main/pg_hba.conf``), comment
out any line that starts with ``local all``, and add a line like
this::

 local   all   all  trust

Then restart postgresql.


Next Steps: Run the Demo, or Create a Custom App
================================================

If you want to run the :doc:`OpenBlock demo app <packages/obdemo>`, proceed
with the rest of this document.

Or, you can dive right in to :doc:`custom`.


Setting up the demo
===================

If you want to create a new project immediately, you can now skip to
:doc:`custom`.  If you want to play with a demo that uses Boston data,
read on.

You'll want to edit the demo's django settings at this point,
or at least look at it to get an idea of what can be
configured::

    $ favorite_editor src/openblock/obdemo/obdemo/settings.py

Activate your virtualenv::

    $ source bin/activate

Now you can set up the database(s). If you're using the default
configuration, where there's a user named 'openblock' and a single
database also named 'openblock', run these commands::

    $ sudo -u postgres createuser --createdb openblock
    $ sudo -u postgres createdb -U openblock --template template_postgis


Starting the Test Server
------------------------

There's a manage.py script in src/obdemo/obdemo/manage.py.
Set your DJANGO_SETTINGS_MODULE environment variable and run it,
then visit http://127.0.0.1:8000/ in your Web browser to see the site in action (with no data)::

  $ export DJANGO_SETTINGS_MODULE=obdemo.settings
  $ ./src/obdemo/obdemo/manage.py runserver

.. _demodata:

Loading Demo Data
-----------------

OpenBlock is pretty boring without data!  You'll want to load some
:ref:`geographic data <locations>` and some local news.  We've
included some example data for Boston, MA, and loader scripts you can
use to start with if you don't have all of your local data on hand yet.

Set your DJANGO_SETTINGS_MODULE environment variable before you begin.
If you are loading the data into a different project, set this
variable accordingly -- e.g. ``myblock.settings`` instead of
``obdemo.settings``::

  $ export DJANGO_SETTINGS_MODULE=obdemo.settings

First you'll want to load Boston geographies. This will take several minutes::

  $ cd src/openblock
  $ obdemo/bin/import_boston_zips.sh
  $ obdemo/bin/import_boston_hoods.sh
  $ obdemo/bin/import_boston_blocks.sh

Then bootstrap some news item :ref:`schema definitions <newsitem-schemas>`::

  $ obdemo/bin/add_boston_news_schemas.sh

Then fetch some news from the web, this will take a few minutes::

  $ obdemo/bin/import_boston_news.sh


For testing random data you might also want to try
``obdemo/bin/random_news.py 10``
... where 10 is the number of random articles to generate.  You must
first have some blocks in the database; it will assign randomly
generated local news articles to randomly chosen blocks.

Deployment
==========

Most people use apache and mod_wsgi for deploying Django apps.
If you're deploying obdemo, there's a suitable wsgi script at
obdemo/wsgi/obdemo.wsgi.  Otherwise, see
http://docs.djangoproject.com/en/1.1/howto/deployment/modwsgi/

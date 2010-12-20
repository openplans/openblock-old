====================
Installing OpenBlock
====================

These instructions cover manual installation of OpenBlock in a similar
configuration to `the OpenBlock demo site
<http://demo.openblockproject.org>`_.

There are a lot of steps involved - but if you go this route, you'll
know how everything's done and you can adjust things as needed for
your system.

If you just want the demo running as quickly as possible, and don't
care to know all the details of how it's done, try following the
:doc:`demo_setup` instructions instead.

.. _support:

If you have problems...
=======================

Please drop a line to the `ebcode google group <http://groups.google.com/group/ebcode>`_
or visit the openblock irc channel ``#openblock`` on freenode with any problems you encounter.  We're glad to help.


.. _requirements:

System Requirements
===================

Linux, OSX, or some other Unix flavor.

Windows is not supported by the OpenBlock team, and may never be; but
patches are welcome :)

You also need:

* python 2.6  (2.7 might work; 2.5 is too old)
* Postgresql 8.3, 8.4, or 9.0
* PostGIS 1.4 or 1.5
* lxml, sometimes called python-lxml (OR libxml2 and libxslt)
* libgdal
* git
* subversion
* wget
* unzip
* `virtualenv <http://pypi.python.org/pypi/virtualenv>`_


For system-specific lists of packages to install, see
http://developer.openblockproject.org/wiki/InstallationRequirements
and let us know if your system isn't listed there!

Don't forget ldconfig!
----------------------

Typically after installing libraries, you will need to run this command::

  $ sudo ldconfig

in order for new libraries to be found while building software.

Install the base software
============================

See the :ref:`requirements` above and make sure you have
everything installed.

Create a virtualenv that will contain the openblock software and all
its python dependencies::

    $ virtualenv openblock
    $ cd openblock

"Activate" your virtualenv - this makes sure that all python commands
will use your new virtual environment::

    $ source bin/activate

Activating also sets the ``$VIRTUAL_ENV`` environment variable, which
we can use as a convenient base to be sure that we run commands in the
right directory.

We'll be using ``pip`` to install some software, so make sure it's
installed (recent versions of virtualenv do this for you)::

    $ easy_install pip

Check out the openblock software::

    $ mkdir src/
    $ git clone git://github.com/openplans/openblock.git src/openblock


Install lxml
------------

The easy way
~~~~~~~~~~~~

It's easiest to install your platform's package for lxml globally, if
it has one. For example, on ubuntu::

    $ sudo apt-get install python-lxml

If that works, you can skip to :ref:`gdal`.

The slightly harder way
~~~~~~~~~~~~~~~~~~~~~~~

If your platform doesn't have a ready-made lxml package, or if you
prefer to build your own, you'll need the libxml2 and libxslt
development libraries, and then install lxml yourself.  For example, on ubuntu
you can do::

    $ sudo apt-get install libxml2 libxml2-dev libxslt libxslt-dev
    $ sudo ldconfig
    $ sudo pip install lxml

.. _gdal:

Install GDAL
------------

The easy way
~~~~~~~~~~~~

GDAL installation isn't covered in detail by the GeoDjango install
docs.

The easiest thing to do is check if your operating system already
provides a ready-made python GDAL package. For example, on Ubuntu,
this will work::

   $ sudo apt-get install python-gdal

If that works, you can skip to :ref:`pythonreqs`.

GDAL the hard way
~~~~~~~~~~~~~~~~~~

*TODO: see if we can contribute this upstream?*

Installing GDAL by hand can be a little tricky, because you have to be careful
about which version you install, and in some cases it may not install
properly without a few extra arguments.

First, get the GDAL development library. On Ubuntu,
this can be installed like::

   $ sudo apt-get install libgdal libdal1-dev
   $ sudo ldconfig

Next, determine which version of the Python GDAL package you need. Try
this command::

   $ gdal-config --version


The output will be a version number like "1.6.3".  Your Python GDAL
package version number needs to match the first two digits.  So if
``gdal-config --version`` tells you "1.6.3", then you need a version
of Python GDAL that's at least 1.6.0, but less than 1.7.  You can use
``pip`` to find an appropriate version, like this::

   $ pip install --no-install "GDAL>=1.6,<1.7a"

Next, remove the bogus setup.cfg file, if any::

   $ rm -f build/GDAL/setup.cfg

Build the python package with some extra options, determined as
described below::

    $ cd $VIRTUAL_ENV/build/GDAL
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



.. _pythonreqs:

Install OpenBlock and all other Python packages
-----------------------------------------------

Pip can install the rest of our Python dependencies with a few
commands::

  $ cd $VIRTUAL_ENV/src/openblock
  $ pip install -r ebpub/requirements.txt -e ebpub
  $ pip install -r ebdata/requirements.txt -e ebdata
  $ pip install -r obadmin/requirements.txt -e obadmin
  $ pip install -r obdemo/requirements.txt -e obdemo


TODO: can we have one req file that includes the others?
then that could be one command.

(We don't install :doc:`packages/ebgeo` because we assume you're not going to
be generating and serving your own map tiles.)


Database Installation
==================================

GeoDjango requires a spatial database.
Follow the `instructions here
<http://docs.djangoproject.com/en/1.2/ref/contrib/gis/install/#postgis>`_,
being sure to use PostGIS as the spatial database.

TODO: it's not at all clear which of those instructions I'm supposed
to follow, as we've already got a fair amount of that stuff.
* need a template

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
configured.  obdemo doesn't come with a settings.py; it comes with a
``settings.py.in`` template that you can copy and edit::

    $ cd $VIRTUAL_ENV/src/openblock/obdemo/obdemo
    $ cp settings.py.in settings.py
    $ favorite_editor settings.py


At minimum, you should change the values of:
* PASSWORD_CREATE_SALT
* PASSWORD_RESET_SALT
* STAFF_COOKIE_VALUE

**TODO: document those**
**TODO: do we still even use the SALT stuff?**

Now you can set up the database(s).  Openblock supports multiple
databases; they have to be synced in the correct order. With the
default database configuration, where there are three configured
back-ends but all are pointing to an ``openblock`` database with an
``openblock`` user, you can create the (empty) database with these commands::

    $ sudo -u postgres createuser --createdb openblock
    $ sudo -u postgres createdb -U openblock --template template_postgis openblock

If you decide to split users and/or metros into separate databases,
you'll have to run another ``createdb`` command for each one.

Now you're ready to initialize your database(s). You have to specify
all configured databases even if they all use the same database in
settings.py::

    $ cd $VIRTUAL_ENV/src/openblock/obdemo/obdemo
    $ ./manage.py syncdb --database=users
    $ ./manage.py syncdb --database=metros
    $ ./manage.py syncdb --database=default

Finally, there's one database trigger that needs to be set up, but --
due to a `Django bug <http://code.djangoproject.com/ticket/13826>`_ --
isn't created automatically.  We'll fix this with one command::

    $ ./manage.py dbshell --database=default < ../../ebpub/ebpub/db/sql/location.sql


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

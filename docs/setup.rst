==========================
Preparing Your System
==========================

These instructions cover manual installation of the prerequisites for
OpenBlock.

There are a lot of steps involved - but if you go this route, you'll
know how everything's done and you can adjust as needed for
your system.

If you just want the Boston demo running as quickly as possible, and don't
care about the gory details, you might try following the :ref:`demo_quickstart`
instructions instead.

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

... in order for new libraries to be found while building software.


.. _database_installation:

Database Installation
==================================

GeoDjango requires a spatial database; more specifically, OpenBlock
requires PostGIS.  You can install it on the same host as OpenBlock,
or on a database server.

OpenBlock is known to work with Postgresql 8.3, 8.4, or 9.0, and PostGIS
1.4 or 1.5.



.. _postgis_server:

PostGIS: On Another Server
--------------------------

If you're going to run postgresql on the same system where you're
installing openblock, skip ahead to :ref:`postgis_localhost`.

If you're going to run postgresql on a separate server, then --
assuming your database administrator can install postgis as per
:ref:`template_setup`.  -- you'll only need the postgresql client
packages.  On Ubuntu, for example, you can run::

   $ sudo apt-get install postgresql-client

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
may have some useful information.

For example, on Ubuntu 10.04 or 10.10, the easiest way to install is
to do::

   $ sudo apt-get install postgresql-8.4-postgis


You'll also need to make sure that the ``openblock`` user can connect
to the postgresql database.  The
easiest way to allow this is to find the ``pg_hba.conf`` file
under ``etc`` (the precise location varies, but for postgresql
8.4 on Ubuntu it's ``/etc/postgresql/8.4/main/pg_hba.conf``), comment
out any line that starts with ``local all``, and add a line like
this::

 local   all   all  trust

Then restart postgresql, and continue to :ref:`template_setup`

.. _template_setup:

PostGIS: template setup
-----------------------

Regardless of whether you run postgresql locally or on another host,
you'll want a PostGIS template database.  Some platforms install this
automatically for you, some don't.

You (or your database admin) should follow directions from
http://docs.djangoproject.com/en/1.2/ref/contrib/gis/install/#creating-a-spatial-database-template-for-postgis
and be sure to heed the **Note** about varying names and locations of
the relevant files.



Installing the base software
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


Installing lxml
---------------

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

Installing GDAL
---------------

The easy way
~~~~~~~~~~~~

GDAL installation isn't covered in detail by the GeoDjango install
docs.

The easiest thing to do is check if your operating system already
provides a ready-made python GDAL package. For example, on Ubuntu,
this will work::

   $ sudo apt-get install python-gdal

If that works, you can skip to :ref:`next steps <postinstall>`.

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



.. _postinstall:

Next Steps: Install the Demo, or Create a Custom App
=====================================================

If you want to run the OpenBlock demo app (just like http://demo.openblockproject.org), proceed
with :ref:`detailed_demo_instructions`.

Or, you can dive right in to :doc:`custom`.


Deployment
==========

Most people use apache and mod_wsgi for deploying Django apps.
If you're deploying obdemo, there's a suitable wsgi script at
obdemo/wsgi/obdemo.wsgi.  Otherwise, see
http://docs.djangoproject.com/en/1.1/howto/deployment/modwsgi/

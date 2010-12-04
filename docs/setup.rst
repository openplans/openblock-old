====================
Installing OpenBlock
====================

These instructions cover manual installation of OpenBlock in a similar
configuration to `the OpenBlock demo site
<http://demo.openblockproject.org>`_.

Unlike the :doc:`demo_setup` instructions, there are more manual steps
and more prerequisites to install yourself.

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
* libxml2
* libxslt
* git
* subversion
* `virtualenv <http://pypi.python.org/pypi/virtualenv>`_


For system-specific lists of packages to install, see
http://developer.openblockproject.org/wiki/InstallationRequirements
and let us know if your system isn't listed there!

Installing the base software
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

TODO: manually do everything in ``obadmin post_bootstrap``:

  * install_gdal
  * install_requirements
  * apply_patches
  * install_ob_packages
  * install_manage_script
  * install_app


Database Installation
==================================

GeoDjango requires a spatial database. 
Follow the `instructions here
<http://docs.djangoproject.com/en/1.2/ref/contrib/gis/install/#>`_,
being sure to use PostGIS as the spatial database.

PostGIS: On Localhost
---------------------

If you're not going to run postgresql on the same system where you're
installing openblock, skip ahead to :ref:`postgis_server`.

OpenBlock is known to work with Postgresql 8.3, 8.4, or 9.0, and PostGIS
1.4 or 1.5.

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

.. _postgis_server:

PostGIS: On Another Server
--------------------------

In this case, assuming your database administrator can install postgis
for you, you'll only need the postgresql client packages.  On Ubuntu,
for example, this would be ``postgresql-client``.

You'll have to work out any connection or authentication issues with
your database admin.

.. _baseinstall:


Problems?
=========

Please drop a line to the `ebcode google group <http://groups.google.com/group/ebcode>`_
or visit the openblock irc channel ``#openblock`` on freenode with any problems you encounter.  We're glad to help.

If you are having trouble with the installation of a particular package, you may want to try installing it by hand or seeing if your distribution offers a prebuilt package.  If you rerun the installation process, it should skip over anything you've done yourself.


Setting up the demo
===================

If you want to create a new project immediately, you can now skip to
:doc:`custom`.  If you want to play with a demo that uses Boston data,
read on.

Optionally, you can edit the demo's django settings at this point. 
It's a good idea to look at it, at least to get an idea of what can be
configured::

    $ favorite_editor src/openblock/obdemo/obdemo/settings.py

Activate your virtualenv::

    $ source bin/activate

Now you can set up the database(s).
TODO: unpack these two commands::

    $ sudo -u postgres bin/oblock setup_dbs
    $ bin/oblock app=obdemo sync_all

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

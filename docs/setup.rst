=====================
Setting up OpenBlock
=====================

This is an annotated version of the :ref:`Quickstart <quickstart>` and the steps that are performed by the ``bootstrap_demo.sh`` script.

.. _baseinstall:

Installing the base software
============================

See the :ref:`requirements` section and make sure you have
everything installed, including setting up database access.

Create a directory that will contain your openblock install.  This will become a `virtualenv <http://virtualenv.openplans.org/>`_ containing the software and its dependencies.::

    $ mkdir openblock
    $ mkdir openblock/src
    $ cd openblock

Check out the software::

    $ git clone git://github.com/openplans/openblock.git src/openblock

You should have a ``bootstrap.py`` script in the root of your openblock checkout. 
Run it.  This will set up the virtualenv and install the OpenBlock software and 
its python requirements in the folder it is called from::

   $ python src/openblock/bootstrap.py


Problems?
=========

Please drop a line to the `ebcode google group <http://groups.google.com/group/ebcode>`_ or visit the openblock irc channel #openblock on freenode with any problems you encounter.  We're glad to help.

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

Now you can set up the database::

    $ sudo -u postgres bin/oblock setup_dbs
    $ bin/oblock app=obdemo sync_all

Starting the Test Server
------------------------

A django manage.py should have been created in the root of your install.  Run it and visit http://127.0.0.1:8000/ in your Web browser to see the site in action (with no data)::

  $ ./manage.py runserver


.. _demodata: 

Loading Demo Data
-----------------

OpenBlock is pretty boring without data!  You'll want to load some
:ref:`geographic data <locations>` and some local news.  We've
included some example data for Boston, MA and loader scripts you can
use to start with if you don't have all of your data on hand yet.

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

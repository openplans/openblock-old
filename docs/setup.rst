=====================
Setting up OpenBlock
=====================

This is an annotated version of the :ref:`Quickstart <quickstart>` and the steps that are performed by the bootstrap_demo.sh script.

.. _baseinstall:

Installing the base software
============================

See the :ref:`requirements` section and make sure you have
everything installed.

Create a location that will contain your openblock install.  This will become a `virtualenv <http://virtualenv.openplans.org/>`_ containing the software and its dependencies.::

    $ mkdir openblock
    $ mkdir openblock/src
    $ cd openblock

Check out the software::

    $ git clone git://github.com/openplans/openblock.git src/openblock

You should have a 'bootstrap.py' script in the root of your openblock checkout. 
Run it.  This will set up the virtualenv and install the OpenBlock software and 
its python requirements in the folder it is called from::

   $ python src/openblock/bootstrap.py


Problems?
=========

Please drop a line to the `ebcode google group <http://groups.google.com/group/ebcode>`_ or visit the openblock irc channel #openblock on freenode with any problems you encounter.  We're glad to help.

If you are having trouble with the installation of a particular package, you may want to try installing it by hand or seeing if your distribution offers a prebuilt package.  If you rerun the installation process, it should skip over anything you've done yourself.

Setting up the demo
===================

Optionally, you can edit the demo's django settings at this point. 
It's a good idea to look at it, at least to get an idea of what can be
configured::

    $ favorite_editor src/openblock/obdemo/obdemo/settings.py

Activate your virtualenv:: 

    $ source bin/activate 

Now you can set up the database::

    $ sudo -u postgres oblock setup_dbs
    $ oblock sync_all

Starting the Test Server
------------------------

A django manage.py should have been created in the root of your install.  Run it and visit http://127.0.0.1:8000/ in your Web browser to see the site in action (with no data)::

  $ ./manage.py runserver


Loading Demo Data
-----------------

OpenBlock is pretty boring without data!  You'll want to load some
geographic data and some local news.

First you'll want to load Boston geographies. This will take several minutes::

  $ cd src/openblock
  $ obdemo/bin/import_boston_zips.sh
  $ obdemo/bin/import_boston_hoods.sh
  $ obdemo/bin/import_boston_blocks.sh

Then bootstrap some news item schema definitions::

  $ obdemo/bin/add_boston_news_schemas.sh

Then fetch some news from the web, this will take a few minutes::

  $ obdemo/bin/import_boston_news.sh


For testing random data you might also want to try
``obdemo/bin/random_news.py 100``
... where 100 is the number of random articles to generate.  You must
first have some locations in the database; it will assign randomly
generated local news articles to randomly chosen locations.

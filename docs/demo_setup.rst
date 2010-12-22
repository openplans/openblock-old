=========================================
Installing and Setting Up the Demo Site
=========================================

These instructions will install the software in a similar configuration to 
`the OpenBlock demo site <http://demo.openblockproject.org>`_ in an isolated 
python environment using `virtualenv <http://pypi.python.org/pypi/virtualenv>`_.


.. _demo_quickstart:

Demo Quickstart
===================

Warning
-------

We use several scripts (python and bash) to automate a lot of the
installation, configuration, and data bootstrapping. *If it works for
you* this can be the quickest way to test OpenBlock on your system,
but we are not trying to make it work on all possible variations of linux,
OSX, etc. - so, *caveat emptor*.

Installation
------------

First make sure you have the :ref:`requirements` installed.

Next make sure you have :ref:`installed PostGIS <postgis_localhost>`
on the same system (our installer script doesn't support putting
postgis on a remote host).

(You can skip the rest of the :doc:`setup` document; everything else
you need will be done automatically by the install scripts.)

Now get the OpenBlock code::

 $ mkdir openblock
 $ cd openblock
 $ mkdir src
 $ git clone git://github.com/openplans/openblock.git src/openblock

The obdemo package contains a shell script that builds the rest of the
system and loads demonstration data (for Boston, MA) into the system::

 $ src/openblock/obdemo/bin/bootstrap_demo.sh

Wait 10 minutes or so; a lot of output will scroll by.
If it finishes successfully, you should see a message like::

 Demo bootstrap succeeded!

Now you can start the server from the root of your install::

 $ ./manage.py runserver

If all goes well, you should be able to visit the demo site at:
http://localhost:8000 

(If you're curious how the bootstrap script worked, have a look at
the source of ``obdemo/bin/bootstrap_demo.sh`` and the underlying
Paver script in :doc:`packages/obadmin`.)


If you run into trouble
-----------------------

If you encounter problems, double check that you have the basic system
:ref:`requirements` installed.

Then you can try doing the part that failed by hand, and then
re-running ``bootstrap_demo.sh``.

Anytime you re-run ``bootstrap_demo.sh``, eg. if
you've got your system so broken that you want to start from scratch,
you may consider wiping out your existing database by giving the ``-r``
option::

 $ src/openblock/obdemo/bin/bootstrap_demo.sh -r

Note that this will completely and permanently wipe out your openblock
database, so think twice!

Finally, be aware (again) that ``bootstrap_demo.sh`` may simply not
work on your system!  Try the :ref:`detailed_demo_instructions` below.


For more help, you can try the ebcode group:
http://groups.google.com/group/ebcode
or look for us in the #openblock IRC channel on irc.freenode.net.


.. _detailed_demo_instructions:

Step-By-Step Demo Installation
==============================

These instructions do basically the same things as the
:ref:`demo_quickstart` above.

Basic Setup
-----------

First, follow **all** the instructions in the :doc:`setup` document.

.. _pythonreqs:

Installing Python packages
--------------------------------------------------

If you followed the :doc:`setup` instructions properly,
you've already got a virtualenv ready.  Go into it and activate it,
if you haven't yet::

  $ cd path/to/your/virtualenv
  $ source bin/activate

Check out the OpenBlock software::

    $ mkdir -p src/
    $ git clone git://github.com/openplans/openblock.git src/openblock

``Pip`` can install OpenBlock and the rest of our Python dependencies with a few
commands::

  $ cd $VIRTUAL_ENV/src/openblock
  $ pip install -r ebpub/requirements.txt -e ebpub
  $ pip install -r ebdata/requirements.txt -e ebdata
  $ pip install -r obadmin/requirements.txt -e obadmin
  $ pip install -r obdemo/requirements.txt -e obdemo


(TODO: can we have one req file that includes the others?
then that could be one command.)

(We don't install :doc:`packages/ebgeo` because we assume you're not going to
be generating and serving your own map tiles.)


Editing Settings
----------------

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

Database Initialization
-----------------------

Django supports using multiple databases for different model data.
OpenBlock can use this feature if you want.

One caveat is that they must be synced in the correct order. With the
default demo database configuration, where there are three configured
back-ends but all are pointing to the same ``openblock`` database with
an ``openblock`` user, you can create the (empty) database with these
commands::

    $ sudo -u postgres createuser --createdb openblock
    $ sudo -u postgres createdb -U openblock --template template_postgis openblock

If you later decide to split users and/or metros into separate databases,
you'd have to run another ``createdb`` command for each one.

Now you're ready to initialize your database tables. You have to
specify all configured databases even if they all use the same
database in settings.py. The users database has to come first::

    $ cd $VIRTUAL_ENV/src/openblock/obdemo/obdemo
    $ ./manage.py syncdb --database=users
    $ ./manage.py syncdb --database=metros
    $ ./manage.py syncdb --database=default

Finally, there's one database trigger that needs to be set up, but --
due to a `Django bug <http://code.djangoproject.com/ticket/13826>`_ --
it isn't created automatically.  We'll fix this with one command::

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
(If you are loading the data into a different project, set this
variable accordingly -- e.g. ``myblock.settings`` instead of
``obdemo.settings``)::

  $ export DJANGO_SETTINGS_MODULE=obdemo.settings

First you'll want to load Boston geographies. This will take several minutes::

  $ cd src/openblock
  $ obdemo/bin/import_boston_zips.sh
  $ obdemo/bin/import_boston_hoods.sh
  $ obdemo/bin/import_boston_blocks.sh

Then bootstrap some news item :ref:`schema definitions <newsitem-schemas>`::

  $ obdemo/bin/add_boston_news_schemas.sh

Then fetch some news from the web, this will take several minutes::

  $ obdemo/bin/import_boston_news.sh


For testing with random data you might also want to try
``obdemo/bin/random_news.py 10`` ...
where 10 is the number of random articles to generate.  You must
first have some blocks in the database; it will assign randomly
generated local news articles to randomly chosen blocks.

Next Steps
==========

Now that you have the demo running, you might want to add some more
:doc:`custom content types <schemas>` to it, and write some
:doc:`scraper scripts <scraper_tutorial>` to populate them.

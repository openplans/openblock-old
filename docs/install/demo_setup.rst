=========================================
Installing and Setting Up the Demo Site
=========================================

These instructions will install the software in a similar configuration to 
`the OpenBlock demo site <http://demo.openblockproject.org>`_.  To
start a custom application instead, please see :doc:`custom`.

(You can skip this if you are :doc:`cloning an OpenBlock AMI <aws>`.)

.. _demo_quickstart:

.. _detailed_demo_instructions:

Step-By-Step Demo Installation
==============================

Basic Setup
-----------

First, follow **all** the instructions in the :doc:`setup` document and :doc:`base_install`

If you followed the :doc:`base_install` instructions properly,
you've already got a virtualenv ready.  Go into it and activate it,
if you haven't yet:

.. code-block:: bash

  $ cd path/to/your/virtualenv
  $ source bin/activate


.. _pythonreqs:


Installing obdemo - stable release
----------------------------------

``obdemo`` is included as part of :ref:`stable_base_install`.

You'll then want to make a copy of the skeleton settings file for
editing, which lives at ``$VIRTUAL_ENV/lib/python2.*/site-packages/obdemo/settings.py.in``.

Installing obdemo for development
---------------------------------

You can work on the latest development code of ``obdemo`` and its
dependencies like this, assuming you've already taken care of
:ref:`development_base_install`:

.. code-block:: bash

  $ cd $VIRTUAL_ENV/src/openblock
  $ pip install -r obdemo/requirements.txt
  $ pip install -e obdemo


Editing Settings
----------------

You'll want to edit the demo's django settings at this point,
or at least look at it to get an idea of what can be
configured.  There is also some :doc:`configuration documentation <configuration>`
you should look at.


``obdemo`` doesn't come with a settings.py; it comes with a
``settings.py.in`` template that you can copy and edit.

(If you've installed OpenBlock sources from git, this file will be at
``$VIRTUAL_ENV/src/openblock/obdemo/obdemo/settings.py.in``. If you've
installed a stable release from pypi, it will be at
``$VIRTUAL_ENV/lib/python2.*/site-packages/obdemo/settings.py.in``.)

.. code-block:: bash

    $ cd path/to/obdemo
    $ cp settings.py.in settings.py
    $ favorite_editor settings.py

At minimum, you should change the values of:

* ``PASSWORD_CREATE_SALT`` - this is used when users create a new account.
* ``PASSWORD_RESET_SALT`` - this is used when users reset their passwords.
* ``STAFF_COOKIE_VALUE`` - this is used for allowing staff members to see
  some parts of the site that other users cannot, such as :doc:`types
  of news items <../main/schemas>` that you're still working on.

You'll also want to think about :ref:`base_layer_configs`.


Database Initialization
-----------------------

You should already have taken care of :ref:`database_installation`.
Create the (empty) database with this command:

.. code-block:: bash

    $ sudo -u postgres createdb -U openblock --template template_postgis openblock

Now initialize your database tables:

.. code-block:: bash

    $ export DJANGO_SETTINGS_MODULE=obdemo.settings
    $ django-admin.py syncdb --migrate

(The --migrate option is important; it loads some initial data that
openblock depends on including stored procedures, and some default
:doc:`Schemas <../main/schemas>` that you can try out, modify, and delete as
needed.)

This will also prompt you to create an administrative user, which is a
good idea.

Starting the Test Server
------------------------

Run these commands to start the test server:

.. code-block:: bash

  $ export DJANGO_SETTINGS_MODULE=obdemo.settings
  $ django-admin.py runserver
    ...
    Development server is running at http://127.0.0.1:8000/

You can now visit http://127.0.0.1:8000/ in your Web browser to see
the site in action (with no data). You can log in to view the
administrative site at http://127.0.0.1:8000/admin/ .

.. _demodata:

Loading Demo Data
-----------------

OpenBlock is pretty boring without data!  You'll want to load some
:doc:`geographic data <geodata>` and some local news.  We've
included some example data for Boston, MA, and scraper scripts you can
use to start with if you don't have all of your local data on hand yet.

Set your DJANGO_SETTINGS_MODULE environment variable before you begin:

.. code-block:: bash

  $ export DJANGO_SETTINGS_MODULE=obdemo.settings

First you'll want to load Boston geographies. This will take several minutes:

.. code-block:: bash

  $ django-admin.py import_boston_zips
  $ django-admin.py import_boston_hoods
  $ django-admin.py import_boston_blocks

Then fetch some news from the web, this will take several minutes:

.. code-block:: bash

  $ django-admin.py import_boston_news


For testing with random data you might also want to get the
``misc`` directory from the OpenBlock source code, and try the
``random-news`` script like so:

.. code-block:: bash

  $ src/openblock/misc/bin/random_news.py 10 local-news

... where 10 is the number of random articles to generate, and
'local-news' is a :doc:`Schema slug <../main/schemas>`.  You must
first have some blocks in the database; it will assign randomly
generated local news articles to randomly chosen blocks.

Next Steps
==========

Now that you have the demo running, you might want to add some more
:doc:`custom content types <../main/schemas>` to it, and write some
:doc:`scraper scripts <../main/scraper_tutorial>` to populate them.

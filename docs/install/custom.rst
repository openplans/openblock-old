==========================================
Creating a Custom Site Based on OpenBlock
==========================================

If you want to do something much different than
:doc:`../packages/obdemo`, you're better off starting from scratch with a
custom Django project. We provide a script that will get you started with
a skeleton app that you can edit.

(You can skip this if you are :doc:`cloning an OpenBlock AMI <aws>`.)

Setting up the app
==================


Basic Setup
-----------

First, follow **all** the instructions in the :doc:`setup` document and :doc:`base_install`

If you followed the :doc:`base_install` instructions properly,
you've already got a virtualenv ready.  Go into it and activate it,
if you haven't yet::

  $ cd path/to/your/virtualenv
  $ source bin/activate


Create Custom App Package
-------------------------

Now do the following to create a new OpenBlock project.  **Note**:
Your project name should be suitable for use as a python module name;
i.e. no spaces etc.  Here we assume the project name is `myblock`::

    $ cd $VIRTUAL_ENV/src
    $ paster create -t openblock myblock

After answering a few questions, this will create a bare-bones Django
project in the folder you specified.  Next, install the project into 
your environment::

    $ cd myblock
    $ python setup.py develop
    ...


What You Get
-------------

The created package is a minimal Django project that includes:

* ``settings.py`` you can :ref:`edit <custom_settings>`.
* ``urls.py`` that wraps :doc:`ebpub's <../packages/ebpub>` URLs; you
  can override individual views here, add custom views and other
  Django apps, etc.
* ``manage.sh``, a tiny wrapper around ``manage.py`` / ``django-admin.py`` that saves
  you the trouble of activating your virtualenv or exporting ``DJANGO_SETTINGS_MODULE``.
* ``templates/homepage.html``, an example of overriding one of
  ``ebpub``'s templates, edit as you like.
* ``wsgi/<projectname>.wsgi``, suitable for
  :doc:`deploying your project under Apache and mod_wsgi <../main/deployment>`.
  It takes care of finding the containing
  virtualenv and the ``DJANGO_SETTINGS_MODULE`` automatically.


.. _custom_settings:

Adjust Django Settings
----------------------

Your django settings are located in settings.py within your project.  You should review these
and make adjustments based on your setup::

    $ favorite_editor myblock/settings.py
    ...

Read more about :doc:`important settings you can/should customize <configuration>`.

If you plan to use a remote database or have other changes to database
connection information, make sure you change them in your settings.py.
See :ref:`postgres_auth` and be sure everything works
before you proceed.

Create and Initialize the Database
----------------------------------

Now, as usual with Django projects, you'll need to create and
initialize your database.  If you haven't changed the default
database settings, and if you've followed the :ref:`template_setup`
instructions, then the database creation command would simply be::

    $ sudo -u postgres createdb -U openblock --template template_postgis openblock_myblock

If you have a different postgresql setup, for example you're using a
different user than ``openblock``, just change the -U option
accordingly.

Now initialize your database tables::

    $ export DJANGO_SETTINGS_MODULE=myblock.settings
    $ django-admin.py syncdb --migrate

(The --migrate option is important; it loads some initial data that
openblock depends on including stored procedures, and some default
:doc:`Schemas <../main/schemas>` that you can try out, modify, and delete as
needed.)

This will also prompt you to create an administrative user, which is a
good idea.

Starting the Test Server
------------------------

Run django's test server using your project's settings and visit http://127.0.0.1:8000/ in your Web browser to see the site in action (with no data)::

    $ export DJANGO_SETTINGS_MODULE=myblock.settings
    $ django-admin.py runserver
    ...
    Development server is running at http://127.0.0.1:8000/

You can now visit http://127.0.0.1:8000/ in your Web browser to see
the site in action (with no data). You can log in to view the
administrative site at http://127.0.0.1:8000/admin/ .


Loading Data: Things You Will Need
==================================

To get anything useful out of your site, at minimum you will need the following:

 1. Geographic data for your area. See :doc:`geodata`.

 2. Sources of news data to feed in.

    a. Configure the system with schemas for them.
       See :doc:`../main/schemas` and ebpub docs for :ref:`newsitem-schemas`.

    b. Write scraper scripts to retrieve news from your news sources and load
       it into the database. See the :doc:`../main/scraper_tutorial`, :doc:`../packages/ebdata`
       and http://developer.openblockproject.org/wiki/ScraperScripts .

 3. Optionally, customize the look and feel of the site.
    See the ebpub docs for :ref:`custom-look-feel`.

Gathering all this data and feeding it into the database can be a bit
of work at this point.  The ``obdemo/bin/bootstrap_demo.sh`` script
in the openblock source code
does all this for the demo site with Boston data, by calling other
scripts; together, they should serve as a decent example of how to do
things in detail.

If you want to load the demo data into your project, you can use the steps 
listed in :ref:`demodata`. **Note**: use the settings module for your project
instead of `obdemo.settings`.


Additional Resources
--------------------

For more documentation (in progress), see also:
    * http://developer.openblockproject.org/wiki/Data
    * http://developer.openblockproject.org/wiki/Ideal%20Feed%20Formats

Theming
========

One of the main reasons to create a custom app is to override the
OpenBlock look-and-feel.  For more info see :doc:`../main/theming`.

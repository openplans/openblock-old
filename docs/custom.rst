==========================================
Creating a Custom Site Based on OpenBlock
==========================================

If you want to do something much different than
:doc:`packages/obdemo`, you're better off starting from scratch with a
custom Django app. We provide a script that will get you started with
a skeleton app you can edit.

Setting up the app
==================

Begin by following :ref:`the steps to install the base software <baseinstall>`

Next, make sure your environment is activated and then do the following to create 
a new openblock project.  **Note**: Your project name should be suitable for use as a python
module name; ie no spaces etc.  Here we assume the project name is `myblock`::

    $ source bin/activate
    $ cd src
    $ paster create -t openblock myblock

TODO: document what to do with ``manage.py startproject|startapp`` for
people that don't want paster. also, not sure we want to maintain that
paster template.

After answering a few questions, this will create a bare-bones project in the folder you 
specified.  Next, install the project into your environment::

    $ cd myblock
    $ python setup.py develop
    ...

Your django settings are located in settings.py within your project.  You should review these
and make adjustments based on your setup::

    $ <favorite_editor> myblock/settings.py
    ...

Now you can use the openblock command line to create and sync your database.  **Note** the setup_dbs command will only work for a local database.  You will need to create any referenced databases and load postgis by hand otherwise::

    $ cd ../../
    $ sudo -u postgres bin/oblock app=myblock setup_dbs
    $ oblock app=myblock sync_all

TODO: document how to do that without oblock

Starting the Test Server
------------------------

Run django's test server using your project's settings and visit http://127.0.0.1:8000/ in your Web browser to see the site in action (with no data)::

    $ export DJANGO_SETTINGS_MODULE=myblock.settings
    $ django-admin.py runserver
    ...
    Development server is running at http://127.0.0.1:8000/

To create an administrative user, use the standard django createsuperuser command.  This will ask for slightly different information than normal because OpenBlock's user system is based on email::

    $ django-admin.py createsuperuser
    ...
    
You can now log into your openblock instance and visit the administrative site at http://127.0.0.1:8000/admin/


Things You Will Need
====================

To get anything useful out of your site, at minimum you will need the following:

 1. A database of streets in your city; for example
    TIGER/Line files from http://www.census.gov/geo/www/tiger/ .
    See :ref:`blocks`.

 2. Shapefiles with areas of interest - for example,
    neighborhoods, zip codes etc.
    See :ref:`locations`.

 3. Sources of news data to feed in.

    a. Configure the system with schemas for them.
       See :doc:`schemas` and ebpub docs for :ref:`newsitem-schemas`

    b. Write scraper scripts to retrieve news from your news sources and load
       it into the database. See :doc:`packages/ebdata`
       and http://developer.openblockproject.org/wiki/ScraperScripts .

 4. Optionally, customize the look and feel of the site.
    See the ebpub docs for :ref:`custom-look-feel`.

Gathering all this data and feeding it into the database can be a bit
of work at this point.  The ``obdemo/bin/bootstrap_demo.sh`` script
does all this for the demo site with Boston data, and should serve as
a decent example of how to do things in detail.

If you want to load the demo data into your project, you can use the steps 
listed in :ref:`demodata` **Note** use the settings module from your project
instead of `obdemo.settings`


Additional Resources
====================

For more documentation (in progress), see also:
    * http://developer.openblockproject.org/wiki/Data
    * http://developer.openblockproject.org/wiki/Ideal%20Feed%20Formats


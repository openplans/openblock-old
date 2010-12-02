.. OpenBlock documentation master file, created by
   sphinx-quickstart on Mon Oct 25 10:49:32 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


=========
OpenBlock
=========

OpenBlock is a web application that allows users to browse and search
their local area for "hyper-local news" - to see what's going on
recently in the immediate geographic area.

=======
History
=======

OpenBlock began life as the open-source code released by
Everyblock.com in June 2009.  Originally created by Adrian Holovaty
and the Everyblock team, it is now developed as an open-source (GPL)
project at http://openblockproject.org.

Funding for the initial creation of Everyblock and the ongoing
development of OpenBlock is provided by the `Knight Foundation
<http://www.knightfoundation.org/>`_.

.. _requirements:

====================
System Requirements
====================

Linux, OSX, or some other Unix flavor.

* python 2.6  (2.7 might work)
* python-dev  (python development libraries, whatever that's called on your system)
* postgresql
* postgis
* libgdal
* libxml2
* libxslt
* git
* subversion

For system-specific lists of packages to install, see
http://developer.openblockproject.org/wiki/InstallationRequirements
and let us know if your system isn't listed there!


Database Access
---------------

You'll also need to make sure that the ``openblock`` user can connect
to the postgresql database. *We assume you're running the postgresql
server on the same system where you're installing openblock.*  The
easiest way to allow this is to find the ``pg_hba.conf`` file
under ``etc`` (the precise location varies, but for postgresql
8.4 on Ubuntu it's ``/etc/postgresql/8.4/main/pg_hba.conf``), comment
out any line that starts with ``local all``, and add a line like
this::

 local   all   all  trust

Then restart postgresql.

.. _quickstart:

=========================================
Quickstart: Install and Set Up Demo Site
=========================================

These instructions will install the software in a similar configuration to 
`the OpenBlock demo site <http://demo.openblockproject.org>`_ in an isolated 
python environment using `virtualenv <http://pypi.python.org/pypi/virtualenv>`_.

For more detailed instructions, see :doc:`setup`.

First make sure you've taken care of the requirements listed above,
including database access.

Next, create a location where you will install the software and check out the source::

 $ mkdir openblock
 $ mkdir openblock/src
 $ cd openblock
 $ git clone git://github.com/openplans/openblock.git src/openblock
 
The obdemo package contains a shell script that performs a basic setup
and loads demonstration data (for Boston, MA) into the system::

 $ src/openblock/obdemo/bin/bootstrap_demo.sh

Wait 10 minutes or so; a lot of output will scroll by.
If it finishes successfully, you should see a message like::

 Demo bootstrap succeeded!

Now you can start the server from the root of your install::

 $ ./manage.py runserver

If all goes well, you should be able to visit the demo site at:
http://localhost:8000 

If you encounter problems, double check that you have the basic system
requirements installed and then try the step-by-step
instructions in :doc:`setup`.

If for any reason you need to run bootstrap_demo.sh again, eg. if
you've got your system so broken that you want to start from scratch,
you may want to wipe your existing database by giving the "-r"
option::

 $ src/openblock/obdemo/bin/bootstrap_demo.sh -r

Note that this will completely and permanently wipe out your openblock
database, so think twice!

For more help, you can try the ebcode group:
http://groups.google.com/group/ebcode
or look for us in the #openblock IRC channel on irc.freenode.net.


==============
For Developers
==============

This is a Django application, so it's highly recommended that you have
familiarity with the Django Web framework. The best places to learn
are the official `Django documentation <http://docs.djangoproject.com/>`_ and
the free `Django Book <http://www.djangobook.com/>`_. Note that OpenBlock
requires Django 1.2.

Before you dive in, it's *highly* recommended you spend a little bit of
time browsing around http://demo.openblockproject.org and/or
http://EveryBlock.com to get a feel for what this software does.

Also, for a light conceptual background on some of this, particularly
the data storage aspect of :doc:`packages/ebpub`, watch the video "Behind the
scenes of EveryBlock.com" here: http://blip.tv/file/1957362


========
Contents
========

.. toctree::
   :maxdepth: 2
   
   setup
   custom
   schemas
   scraper_tutorial
   running_scrapers
   packages/index
   
..   packages/ebpub

==================
Indices and tables
==================


* :ref:`search`

.. * :ref:`genindex`
.. * :ref:`modindex`

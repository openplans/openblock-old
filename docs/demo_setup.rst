=========================================
Quickstart: Install and Set Up Demo Site
=========================================

These instructions will install the software in a similar configuration to 
`the OpenBlock demo site <http://demo.openblockproject.org>`_ in an isolated 
python environment using `virtualenv <http://pypi.python.org/pypi/virtualenv>`_.

We use several scripts (python and bash) to automate a lot of the
installation, configuration, and data bootstrapping. *If it works for
you* this can be the quickest way to test OpenBlock on your system,
but is not guaranteed to work on all possible variations of linux,
OSX, etc. - so, *caveat emptor*.

If you have problems...
=======================

Please drop a line to the `ebcode google group <http://groups.google.com/group/ebcode>`_
or visit the openblock irc channel ``#openblock`` on freenode with any problems you encounter.  We're glad to help.

You can always try manually installing the part that didn't work, and
then re-running the bootstrap script.

If you decide you'd rather have more control and know everything
that's going on, see the step-by-step instructions in :doc:`setup`.


.. _demo_requirements:

System Requirements
===================

Linux, OSX, or some other Unix flavor.

Windows is not officially supported by the OpenBlock team,
but patches are welcome :)

You also need:

TODO: can we skip libxml2 / libxslt?

* python 2.6  (2.7 might work; 2.5 is too old)
* postgresql and postgis for your spatial database
* libxml2 
* libxslt (may not be required on OSX; not sure)
* git
* subversion

TODO: is that all?

For system-specific lists of packages to install, see
http://developer.openblockproject.org/wiki/InstallationRequirements
and let us know if your system isn't listed there!

The rest of the software needed will be installed automatically.

Database Access
===============

You'll need to make sure that the ``openblock`` user can connect
to the postgresql database. *We assume you're running the postgresql
server on the same system where you're installing openblock.*  The
easiest way to allow this is to find the ``pg_hba.conf`` file
under ``etc`` (the precise location varies, but for postgresql
8.4 on Ubuntu it's ``/etc/postgresql/8.4/main/pg_hba.conf``), comment
out any line that starts with ``local all``, and add a line like
this::

 local   all   all  trust

Then restart postgresql.

Installing
==========

Next, create a location where you will install the software and check out the source::

 $ mkdir openblock
 $ cd openblock
 $ mkdir src
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

If you run into trouble
=======================

If you encounter problems, double check that you have the basic system
:ref:`demo_requirements` installed and then try the step-by-step
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

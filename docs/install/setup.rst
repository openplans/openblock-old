=====================
Preparing Your System
=====================

These instructions cover manual installation of the prerequisites for
OpenBlock and installation of the base Openblock software.

(You can skip this if you are :doc:`cloning our AMI image <aws>`.)

.. _support:

If you have problems...
=======================

Please drop a line to the `ebcode google group <http://groups.google.com/group/ebcode>`_
or visit the IRC channel ``#openblock`` on freenode with any problems you encounter.  We're glad to help.


.. _requirements:

System Requirements
===================

.. admonition:: System-Specific Requirements

  See `System Specific Prerequisites
  <http://developer.openblockproject.org/wiki/InstallationRequirements>`_
  on the developer wiki for specific lists of packages to install
  based on your distribution or OS.

Linux, OSX, or some other Unix flavor is required.  **Windows is not supported**
by the OpenBlock team, and may never be; but patches are welcome :)

Generally, you need:

* python 2.6  (2.7 might work; 2.5 is too old)
* Postgresql 8.3, 8.4, or 9.0
* PostGIS 1.4 or 1.5
* libxml2 and libxslt
* libgdal
* git
* subversion
* wget
* unzip
* `virtualenv <http://pypi.python.org/pypi/virtualenv>`_

Optionally, it may be helpful to install prebuilt packages for the following if your distribution provides them:

* python lxml bindings
* python gdal bindings
* python imaging library (PIL)

See http://developer.openblockproject.org/wiki/InstallationRequirements
for details on installing these on particular operating systems.

(If you don't install these packages globally, the install process will
attempt to build them, which means you need a C compiler, the Python
development libraries, and various other things installed.)

`GeoDjango's platform-specific instructions
<http://docs.djangoproject.com/en/1.3/ref/contrib/gis/install/#platform-specific-instructions>`_
may have some useful information as well, as the majority of OpenBlock's requirements are just those of GeoDjango + PostGIS.


Don't forget ldconfig!
----------------------

Typically after installing libraries, you will need to run this command:

.. code-block:: bash

  $ sudo ldconfig

... in order for new libraries to be found while building software.


.. index:: database, postgis, postgresql
.. _database_installation:

Database Setup
==============

GeoDjango requires a spatial database; more specifically, OpenBlock
requires PostGIS.  This documentation generally assumes you are installing OpenBlock 
and Postgres on the same server.  If you are using a remote server, please 
read :doc:`remote_postgis_server` and make adjustments accordingly.

OpenBlock is known to work with Postgresql 8.3, 8.4, or 9.0, and PostGIS
1.4 or 1.5.

.. _template_setup:

PostGIS template setup
----------------------

Regardless of whether you run postgresql locally or on another host,
you'll want a PostGIS template database.  Some platforms install this
automatically for you, some don't.

You (or your database admin) should follow the instructions for `Creating a Spatial Database Template for PostGIS 
<http://docs.djangoproject.com/en/1.3/ref/contrib/gis/install/#creating-a-spatial-database-template-for-postgis>`_ in the GeoDjango documentation and be sure to heed the **Note** about varying names and locations of the relevant files.


.. _postgres_auth:

Database Access Settings
------------------------

The following instructions (and the default settings) assume that there is 
an ``openblock`` database user which can create a database for use with openblock.  
You can create an openblock user by running:

.. code-block:: bash

    $ sudo -u postgres createuser --createrole --createdb openblock

Depending on your database security setup, you may need to adjust the instructions, settings of postgres and/or settings of openblock.

Postgres administration is beyond the scope of these instructions, but as a quickstart, you can disable postgres security for local users by changing the ``pg_hba.conf`` file under ``etc`` (the precise location varies, but for postgresql
8.4 on Ubuntu it's ``/etc/postgresql/8.4/main/pg_hba.conf``), comment
out any line that starts with ``local all``, and add a line like
this:

.. code-block:: text

 local   all    all  trust

Then restart postgresql.  **This is not suitable for production**.

See `Postgres pg_hba.conf documentation
<http://developer.postgresql.org/pgdocs/postgres/auth-pg-hba-conf.html>`_
or the `postgres wiki <http://wiki.postgresql.org/wiki/Client_Authentication>`_
for more information.

Testing Database Access
~~~~~~~~~~~~~~~~~~~~~~~

If the ``openblock`` user is configured correctly, you should be able to execute:

.. code-block:: bash

    $ createdb -U openblock test_ob_access
    $ dropdb -U openblock test_ob_access


Next Steps
==========

Now that your system is prepped, you are ready to move on to :doc:`base_install`.


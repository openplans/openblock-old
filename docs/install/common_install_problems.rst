Common Installation Problems
============================

This page covers some common installation problems. 

Please feel free to drop a line to the `ebcode google group <http://groups.google.com/group/ebcode>`_
or visit the IRC channel ``#openblock`` on freenode with any problems you encounter.  We're glad to help.  


Python Package Conflicts / Failures
-------------------------------------

Some quick things to check if you have any problems installing any of
the Python package dependencies:

* Make sure your virtualenv is activated. ``$VIRTUAL_ENV`` should
  point to the right directory.

* You should have at least version 1.0 of pip.  Check ``pip --version``

* Make sure pip is installed *in the virtualenv*.  Check the output of
  ``which pip``.

* You should have a recent version of distribute. Try ``easy_install --version``. If it says at least 'distribute 0.6.14', you're OK.

* Don't try to combine the ``pip install -r`` and ``pip install -e``
  commands in one line.  Doing so can result in the wrong version of a dependency.
  (This is a `pip bug <https://github.com/pypa/pip/issues/318>`_.)
  Instead, run them as separate commands; first ``-r``, then ``-e``.

.. _no_site_packages:

Virtualenv: Global packages available or not?
-----------------------------------------------

Note that if you want to install GDAL or LXML the "easy way" as
described below, you *must not* run virtualenv with the
``--no-site-packages`` option, as that will prevent your virtualenv
from being able to find the globally installed libraries.

As of virtualenv 1.7, the default behavior has changed so you now
**must** pass the ``--system-site-packages`` option
in order to use globally installed packages.
*The --no-site-packages option is now the default!*

If you prefer the ``--no-site-packages`` way of using virtualenv,
where it only has access to libraries that you explicitly install,
then you must install GDAL and LXML from source, as described below in
the "hard way" sections.


.. _lxml:

Problems Installing lxml
------------------------

Installing the easy way
~~~~~~~~~~~~~~~~~~~~~~~

It's easiest to install your platform's package for lxml globally, if
it has one. For example, on ubuntu:

.. code-block:: bash

    $ sudo apt-get install python-lxml

(Note that if you want to take this approach, you *must not* run virtualenv
with the ``--no-site-packages`` option, as that will prevent your
virtualenv from being able to use this package.)


The slightly harder way
~~~~~~~~~~~~~~~~~~~~~~~

If your platform doesn't have a ready-made lxml package, or if you
prefer to build your own,
or if you prefer :ref:`an isolated virtualenv <no_site_packages>`,
you'll need the libxml2 and libxslt
development libraries, and then install lxml yourself.  For example, on ubuntu
you can do:

.. code-block:: bash

    $ sudo apt-get install libxml2 libxml2-dev libxslt libxslt-dev build-essential python-dev

And once you have those, on any platform you can do:

.. code-block:: bash

    $ sudo ldconfig
    $ sudo pip install lxml

.. _gdal:

Problems Installing GDAL
------------------------

Installing the easy way
~~~~~~~~~~~~~~~~~~~~~~~

GDAL installation isn't covered in detail by the GeoDjango install
docs.

By far the easiest thing to do is check if your operating system already
provides a ready-made python GDAL package. For example, on Ubuntu,
this will work:

.. code-block:: bash

   $ sudo apt-get install python-gdal

GDAL the hard way
~~~~~~~~~~~~~~~~~~

*TODO: see if we can contribute this upstream?*

Installing GDAL by hand can be a little tricky, because you have to be careful
about which version you install, and in some cases it may not install
properly without a few extra arguments.

First, get the GDAL development library. On Ubuntu,
this can be installed like:

.. code-block:: bash

   $ sudo apt-get install libgdal1-1.6.0 libgdal1-dev build-essential python-dev
   $ sudo ldconfig

Next, make sure you are in your openblock environment and it is activated:

.. code-block:: bash

    $ cd <path_to_openblock>
    $ source bin/activate

Next, determine which version of the Python GDAL package you need. Try
this command:

.. code-block:: bash

   $ gdal-config --version


The output will be a version number like "1.6.3".  Your Python GDAL
package version number  **must match the first two digits**.  So if
``gdal-config --version`` tells you "1.6.3", then you would need a version
of Python GDAL that's at least 1.6.0, but less than 1.7.  Or if
gdal-config tells you that you have 1.7.0, then you would need version
1.7.something of the  Python GDAL package.  You get the idea. You can use
``pip`` to find an appropriate version, like this:

.. code-block:: bash

   $ pip install --no-install "GDAL>=1.6,<1.7a"  # adjust version as needed

Or if ``gdal-config --version`` tells you "1.5.1", then instead you
would need to do ``pip install --no-install "GDAL>=1.5,<1.6a"``. Et
cetera.

Next, remove the bogus setup.cfg file, if any:

.. code-block:: bash

   $ rm -f $VIRTUAL_ENV/build/GDAL/setup.cfg

Build the python package with some extra options, determined as
described below:

.. code-block:: bash

    $ cd $VIRTUAL_ENV/build/GDAL
    $ python setup.py build_ext --gdal-config=gdal-config \
        --library-dirs=/usr/lib \
        --libraries=gdal1.6.0 \
        --include-dirs=/usr/include/gdal \
      install

The correct value for --library-dirs can be determined by running
``gdal-config --libs`` and looking for any output starting with
``-L``.  The correct value for --libraries can be determined with the
same command but looking for output beginning with ``-l``.  The
correct value for ``--include-dirs`` can be determined by running
``gdal-config --cflags`` and looking for output beginning with ``-I``.

Still no luck?
~~~~~~~~~~~~~~

If you get an error like
``/usr/include/gdal/ogr_p.h:94: fatal error: swq.h: No such file or directory``,
that's because of a bug in GDAL.  (See
http://trac.osgeo.org/gdal/ticket/3468 .)

The workaround is to manually install swq.h in the same directory that
contains ogr_p.h, typically somewhere like ``/usr/include/gdal``.  You
can get swq.h for GDAL 1.7 here:
http://svn.osgeo.org/gdal/branches/1.7/gdal/ogr/swq.h

Then try the preceding ``setup.py build_ext`` command again.

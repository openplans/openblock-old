===============
Demo Quickstart
===============

This section will show you how to use our bootstrap scripts to
automatically set up the OpenBlock Boston demo with minimal manual
effort.

Warning
-------

In this quickstart, we use several scripts (python and bash) to
automate a lot of the
installation, configuration, and data bootstrapping. *If it works for
you* this can be the quickest way to try out OpenBlock on your system,
but we are not trying to make it work on all possible variations of linux,
OSX, etc. - so, *caveat emptor*.

Or, if you prefer to have control of how everything's done, follow the
:ref:`detailed_demo_instructions` instead.


Installation
------------

First make sure you have the :ref:`requirements` installed.

Next make sure you have :ref:`installed and configured PostGIS <database_installation>`
on the same system (our installer script doesn't support putting
postgis on a remote host, nor can it modify the postgres config file
for you.)

(You can skip the rest of the :doc:`install/setup` document; everything else
you need will be done automatically by the install scripts.)

Now get the OpenBlock code:

.. code-block:: bash

 $ mkdir openblock
 $ cd openblock
 $ mkdir src
 $ git clone git://github.com/openplans/openblock.git src/openblock

The reason we fetch the code from git is that the bootstrap scripts
aren't part of a python package, and they assume that the whole source
tree is there.

The ``obdemo`` directory in the openblock source code contains a shell script that builds the rest of the
system and loads demonstration data (for Boston, MA) into the system:

.. code-block:: bash

 $ src/openblock/obdemo/bin/bootstrap_demo.sh

Wait 10 minutes or so; a lot of output will scroll by.
If it finishes successfully, you should see a message like::

 Demo bootstrap succeeded!

Now you can start the server:

.. code-block:: bash

 $ export DJANGO_SETTINGS_MODULE=obdemo.settings
 $ django-admin.py runserver

If all goes well, you should be able to visit the demo site at:
http://localhost:8000 

(If you're curious how the bootstrap script worked, have a look at
the source of ``obdemo/bin/bootstrap_demo.sh`` and the underlying
Paver script in :doc:`packages/obadmin`.)


If you run into trouble
-----------------------

If you encounter problems, double check that you have the basic
:ref:`requirements` installed.

Then you can try doing the part that failed by hand, and then
re-running ``bootstrap_demo.sh``.

Anytime you re-run ``bootstrap_demo.sh``, eg. if
you've got your system so broken that you want to start from scratch,
you may consider wiping out your existing database by giving the ``-r``
option:

.. code-block:: bash

 $ src/openblock/obdemo/bin/bootstrap_demo.sh -r  # DANGEROUS!

Note that this will completely and permanently wipe out your openblock
database, so think twice!

Finally, be aware (again) that ``bootstrap_demo.sh`` may simply not
work on your system!  Try the :ref:`detailed_demo_instructions` instead.


For more help, you can try the ebcode group:
http://groups.google.com/group/ebcode
or look for us in the #openblock IRC channel on irc.freenode.net.

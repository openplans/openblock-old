=================================
Installing the Openblock Software
=================================

These steps assume you have fulfilled the requirements and followed the instructions 
in the section :doc:`setup`.

(You can skip this if you are :doc:`cloning an OpenBlock AMI <aws>`.)

.. _virtualenv:

Creating a virtualenv
=====================

Create a "`virtualenv <http://pypi.python.org/pypi/virtualenv>`__" that will contain 
the OpenBlock software and its python dependencies.  (You probably do *not* want to 
do this as root or with sudo). With virtualenv 1.7 or later:

.. code-block:: bash

    $ virtualenv --system-site-packages openblock
    $ cd openblock

Or with virtualenv 1.6 or earlier:

.. code-block:: bash

    $ virtualenv openblock
    $ cd openblock

.. admonition:: Why not --no-site-packages?

  Experienced virtualenv users may wonder why we don't recommend using
  the ``--no-site-packages`` option. See :ref:`no_site_packages` for
  more info.


"Activate" your virtualenv - this makes sure that all python commands
will use your new virtual environment:

.. code-block:: bash

    $ source bin/activate

Activating also sets the ``$VIRTUAL_ENV`` environment variable, which
we can use as a convenient base to be sure that we run commands in the
right directory.

We'll be using ``pip`` to install some software, so make sure it's
installed. Recent versions of virtualenv do this for you, but virtualenv 
< 1.4.1 does not, so we need to make sure.  We also recommend that you 
ensure that the latest version of ``distribute`` is installed:

.. code-block:: bash

    $ easy_install --upgrade pip distribute
    $ hash -r

Note that it's *very* important that ``pip`` is installed *in the
virtualenv*.  If you only have pip installed globally on your system,
*it won't work* and you will get confusing build errors such as
version conflicts, permission failures, etc.

Installing OpenBlock Packages
=============================

You can install either stable releases of the OpenBlock software,
or check out the latest development code.

.. _stable_base_install:

Installing Stable Packages
---------------------------

The latest stable releases of ``ebpub``, ``ebdata``, and ``obadmin``
can be found on `the Python Package Index
<http://pypi.python.org/pypi?%3Aaction=search&term=openblock&submit=search>`_.  To install from these packages, we
will publish a consolidated pip requirements file that will install
*all* the necessary python packages.  These requirements files will be
listed for each release at http://openplans.github.com/openblock/ .

For example, the 1.2 release is at:
http://openplans.github.com/openblock/requirements/openblock-requirements-1.2.txt
and can be installed with this command:

.. code-block:: bash

  $ $VIRTUAL_ENV/bin/pip install -r http://openplans.github.com/openblock/requirements/openblock-requirements-1.2.txt

If you encounter errors during package installation, please see
:doc:`common_install_problems`.


.. _development_base_install:

Installing Development Code
---------------------------

Download the openblock software:

.. code-block:: bash

   $ cd $VIRTUAL_ENV
   $ mkdir -p src/
   $ git clone git://github.com/openplans/openblock.git src/openblock

It takes a few more ``Pip`` commands to install for development, like so:

.. code-block:: bash

  $ cd $VIRTUAL_ENV/src/openblock
  $ pip install -r ebpub/requirements.txt
  $ pip install -e ebpub
  $ pip install -r ebdata/requirements.txt
  $ pip install -e ebdata
  $ pip install -r obadmin/requirements.txt
  $ pip install -e obadmin
  $ pip install -r obdemo/requirements.txt
  $ pip install -e obdemo

If you encounter errors during package installation, please see :doc:`common_install_problems`.

.. _postinstall:


Next Steps: Install the Demo, or Create a Custom App
=====================================================

If you want to run the OpenBlock demo app (just like http://demo.openblockproject.org), proceed
with :ref:`detailed_demo_instructions`.

Or, you can dive right in to :doc:`custom`.

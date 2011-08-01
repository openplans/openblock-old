=================================
Installing the Openblock Software
=================================

These steps assume you have fulfilled the requirements and followed the instructions 
in the section :doc:`setup`.

Creating a virtualenv
=====================

Create a "`virtualenv <http://pypi.python.org/pypi/virtualenv>`_" that will contain 
the OpenBlock software and its python dependencies.  (You probably do *not* want to 
do this as root or with sudo):

.. code-block:: bash

    $ virtualenv openblock
    $ cd openblock

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
ensure that the latest versions of ``pip`` and ``distribute`` are installed:

.. code-block:: bash

    $ easy_install --upgrade pip distribute
    $ hash -r

Note that it's *very* important that ``pip`` is installed *in the
virtualenv*.  If you only have pip installed globally on your system,
*it won't work* and you will get confusing build errors such as
version conflicts, permission failures, etc.

Installing OpenBlock Packages
=============================

Download the openblock software:

.. code-block:: bash

   $ cd $VIRTUAL_ENV
   $ mkdir -p src/
   $ git clone git://github.com/openplans/openblock.git src/openblock

``Pip`` can install OpenBlock and the rest of our Python dependencies with a few
commands:

.. code-block:: bash

  $ cd $VIRTUAL_ENV/src/openblock
  $ pip install -r ebpub/requirements.txt -e ebpub
  $ pip install -r ebdata/requirements.txt -e ebdata
  $ pip install -r obadmin/requirements.txt -e obadmin

If you encounter errors during package installation, please see :doc:`common_install_problems`


.. _postinstall:


Next Steps: Install the Demo, or Create a Custom App
=====================================================

If you want to run the OpenBlock demo app (just like http://demo.openblockproject.org), proceed
with :ref:`detailed_demo_instructions`.

Or, you can dive right in to :doc:`custom`.

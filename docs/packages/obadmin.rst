=========================
obadmin
=========================

Administrative UI, installation and utilities package for OpenBlock.

The oblock command
==================

``oblock`` is a command-line program that gets installed with
obadmin. It provides commands to help install and manage OpenBlock and
its database(s).  This is purely optional, and we've moved away from
recommending it, but the
:doc:`demo setup script <../install/demo_setup>` uses it quite a bit.

Try running ``oblock help`` to see all the available commands.
Each "task" can be run as a subcommand, like ``oblock sync_all``.

obadmin Package
===============

:mod:`obadmin` Package
----------------------

.. automodule:: obadmin
    :members:
    :show-inheritance:

:mod:`pavement` Module
----------------------

.. automodule:: obadmin.pavement
    :members:
    :show-inheritance:

:mod:`skel` Module
------------------

.. automodule:: obadmin.skel
    :members:
    :show-inheritance:

:mod:`testrunner` Module
------------------------

.. automodule:: obadmin.testrunner
    :members:
    :show-inheritance:

Subpackages
-----------

.. toctree::

    obadmin.admin


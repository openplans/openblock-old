====================================
Python API Documentation
====================================

OpenBlock consists of a number of packages, summarized below:

Main Code Packages
====================

.. toctree::
   :maxdepth: 1

   obdemo
   ebpub
   ebdata
   obadmin

:doc:`obdemo`
----------------

The code and configuration used by http://demo.openblockproject.org.
This is useful as an example of how to set up your own site based on
OpenBlock, and is a great place to start.  It primarily uses the ebpub
package, and is set up with Boston, MA as the area of interest.

:doc:`ebpub`
------------

Publishing system for block-specific news, as used by EveryBlock.com.

This is the core of an OpenBlock site, providing the web interface
that users see as well as the underlying data models. You need this.

:doc:`ebdata`
--------------

Code to help write scripts that crawl/parse/import data into ebpub.

:doc:`obadmin`
--------------

Administrative UI, installation and utilities package for OpenBlock.

.. _other_packages:

Other Packages
==============

There are several open-source packages originally released by the
EveryBlock.com team in 2009, but not actively used or maintained by
the OpenBlock core developers.
They have been moved out of OpenBlock itself and into
https://github.com/openplans/openblock-extras

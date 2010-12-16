====================
Main Code Packages
====================

This distribution contains a number of packages, summarized below:


obdemo
======

The code and configuration used by http://demo.openblockproject.org.
This is useful as an example of how to set up your own site based on
OpenBlock, and is a great place to start.  It primarily uses the ebpub
package, and is set up with Boston, MA as the area of interest.

For more information, see :doc:`obdemo`

ebpub
=====

Publishing system for block-specific news, as used by EveryBlock.com.

This is the core of an OpenBlock site, providing the web interface
that users see as well as the underlying data models. You need this.

For more information, see :doc:`ebpub`

ebdata
======

Code to help write scripts that import/crawl/parse data into ebpub.

You *will* need to write such scripts to get OpenBlock to do anything
useful; that is how you feed local news into the system.

For more information, see :doc:`ebdata`

obadmin
=======

Administrative UI, installation and utilities package for OpenBlock.

==================
Other Packages
==================

ebblog
======

The blog application used by http://blog.everyblock.com

Only of interest if you want to bundle a simple blog with your
OpenBlock site; you can probably ignore this.

For more information, see :doc:`ebblog`


ebgeo
=====

The eb map system. This is mostly used for rendering and serving map
tiles with Mapnik. This package is optional and not installed by default.

For more information, see :doc:`ebgeo`


ebinternal
==========

Internal applications for the EveryBlock team.

Most OpenBlock users probably won't need this.
Not used by obdemo.

ebinternal consists of two apps, citypoll and feedback.  citypoll
powers EveryBlock's city voting system, both on EveryBlock.com and on
the iPhone app. feeback manages the feedback received from the
feedback forms at the bottom of almost every page on EveryBlock.com.

For more information, see :doc:`ebinternal`



ebwiki
======

A basic wiki.  

I'm not even sure if this is used on everyblock.com anymore.
Probably not useful to most OpenBlock users.

For more information, see :doc:`ebwiki`


everyblock
===========

This package contains code/templates that are specific to
EveryBlock.com. They were released to fulfill the terms of the grant
that funded EveryBlock's development and are likely not of general
use, with the possible exception of scraper scripts in
everyblock/cities/ and everyblock/states/ which may at least be useful
as examples of how to write scrapers.

For more information, see :doc:`everyblock`

========
Contents
========

.. toctree::
   :maxdepth: 1

   obdemo
   ebpub
   ebdata
   obadmin
   ebblog
   ebgeo
   ebinternal
   ebwiki
   everyblock



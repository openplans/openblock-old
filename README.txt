=========
OpenBlock
=========

OpenBlock is a web application that allows users to browse and search
their local area for "hyper-local news" - to see what's going on
recently in the immediate geographic area.

OpenBlock began life as the open-source code released by
Everyblock.com in June 2009.  Originally created by Adrian Holovaty
and the Everyblock team, it is now developed as an open-source (GPL)
project at http://openblockproject.org.

Funding for the creation of Everyblock and the ongoing development of
OpenBlock is provided by the Knight Foundation.

==============
For Developers
==============

This is a Django application, so it's highly recommended that you have
familiarity with the Django Web framework. The best places to learn
are the official documentation (http://docs.djangoproject.com/) and
the free Django Book (http://www.djangobook.com/). Note that OpenBlock
requires Django 1.1 and as of this writing does not yet work with
Django 1.2 or later.

Before you dive in, it's *highly* recommend you spend a little bit of time
browsing around EveryBlock.com to get a feel for what this software does.

Also, for a light conceptual background on some of this, particularly the
data storage aspect, watch the video "Behind the scenes of EveryBlock.com"
here: http://blip.tv/file/1957362


=============
Contents
=============

This distribution contains a number of packages, summarized below:


obdemo
======

The configuration used by http://demo.openblockproject.org.
This is useful as an example of how to set up your own site
based on OpenBlock, and is a great place to start.
It primarily uses the ebpub package.

For more information, see demo/README.txt


ebblog
======

The blog application used by http://blog.everyblock.com

Only of interest if you want to bundle a simple blog with your
OpenBlock site; you can probably ignore this.

For more information, see ebblog/README.TXT


ebdata
======

Code to help write scripts that import/crawl/parse data into ebpub.

You *will* need to write such scripts to get OpenBlock to do anything
useful; that is how you feed local news into the system.

For more information, see ebdata/README.TXT


ebgeo
=====

The eb map system. This is mostly used for rendering and serving map
tiles with Mapnik.

It also contains some clustering display logic used by ebpub, so you
need to have it installed even if you don't use Mapnik.

For more information, see ebgeo/README.TXT


ebinternal
==========

Internal applications for the EveryBlock team.

Most OpenBlock users probably won't need this.

ebinternal consists of two apps, citypoll and feedback.  citypoll
powers EveryBlock's city voting system, both on EveryBlock.com and on
the iPhone app. feeback manages the feedback received from the
feedback forms at the bottom of almost every page on EveryBlock.com.

For more information, see ebinternal/README.TXT


ebpub
=====

Publishing system for block-specific news, as used by EveryBlock.com.

This is the core of an OpenBlock site, providing the web interface
that users see as well as the underlying data models. You need this.

For more information, see ebpub/README.TXT


ebwiki
======

A basic wiki.  

I'm not even sure if this is used on everyblock.com anymore.
Probably not useful to most OpenBlock users.

For more information, see ebwiki/README.TXT

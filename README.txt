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

Funding for the initial creation of Everyblock and the ongoing
development of OpenBlock is provided by the Knight Foundation
(http://www.knightfoundation.org/).

====================
System Requirements
====================

Linux, OSX, or some other Unix flavor.

python 2.6  (2.7 might work)
python-dev  (python development libraries, whatever that's called on your system)
postgresql
postgis
libgdal
libxml2
libxslt
git

For system-specific lists of packages to install, see
http://developer.openblockproject.org/wiki/InstallationRequirements
and let us know if your system isn't listed there!

=========================================
Quickstart: Install and Set Up Demo Site
=========================================

These instructions will install the software in an isolated 
python environment using virtualenv ( http://pypi.python.org/pypi/virtualenv ).
For detailed instructions and further steps, see obdemo/README.txt::

 $ git clone git://github.com/openplans/openblock.git openblock
 $ cd openblock
 $ cp obdemo/obdemo/real_settings.py.in obdemo/obdemo/real_settings.py

Optionally you can edit obdemo/obdemo/real_settings.py at this stage.
It's a good idea to look at it, at least to get an idea of what can be
configured.

Now install the software and boostrap the Boston data::

 $ obdemo/bin/boostrap_demo.sh

Wait 10 minutes or so, then when it's finished, start the server::

 $ ./manage.py runserver


If all goes well, you should be able to visit the demo site at:
http://localhost:8000 

If you encounter problems, double check that you have the basic system
requirements installed and then have a look at the step-by-step
instructions in obdemo/README.txt.

For more help, you can try the ebcode group:
http://groups.google.com/group/ebcode
or look for us in the #openblock IRC channel on irc.freenode.net.


==============
For Developers
==============

This is a Django application, so it's highly recommended that you have
familiarity with the Django Web framework. The best places to learn
are the official documentation (http://docs.djangoproject.com/) and
the free Django Book (http://www.djangobook.com/). Note that OpenBlock
requires Django 1.2.

Before you dive in, it's *highly* recommend you spend a little bit of
time browsing around http://demo.openblockproject.org and/or
http://EveryBlock.com to get a feel for what this software does.

Also, for a light conceptual background on some of this, particularly the
data storage aspect, watch the video "Behind the scenes of EveryBlock.com"
here: http://blip.tv/file/1957362


==========================================
Creating a Custom Site Based on OpenBlock
==========================================

This is documented in the "Quickstart" section of ebpub/README.TXT.
For an example, have a look in obdemo/ which was set up in that
fashion.

For installation in this case, you can just use the bootstrap.py
script and do the rest of the setup by hand.  You can look at
obadmin/obadmin/pavement.py to get an idea of what needs doing, and/or
modify it for your own use.

Things You Will Need
====================

Details are in ebpub/README.TXT, but briefly to get anything useful
out of your site, at mininum you will need to do the following:

  1. A database of streets in your city; for example
     TIGER/Line files from http://www.census.gov/geo/www/tiger/
     See ebpub/README.TXT

  2. Decide what locations are interesting in your area - for example,
     neighborhoods, zip codes.  Obtain shapefiles of the boundaries of
     those locations, and feed them in. See ebpub/README.TXT

  3. Decide what news sources you want to feed in.

     a. Configure the system with schemas for them. See
     ebpub/README.TXT

     b. Write scraper scripts to retrieve your news sources and feed
     it in. See ebdata/README.TXT and http://developer.openblockproject.org/wiki/ScraperScripts


Yes, this is a lot of work.  For more documentation (in progress), see also:
http://developer.openblockproject.org/wiki/Data
http://developer.openblockproject.org/wiki/Ideal%20Feed%20Formats

The obdemo/bin/bootstrap_demo.sh script does all this for the demo
site.  You can dive into the other scripts that it calls to get more
details on how it all works.


Customizing Look and Feel
=========================

You'll want to read the "Site views/templates" section of
ebpub/README.TXT.


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

For more information, see obdemo/README.txt

ebpub
=====

Publishing system for block-specific news, as used by EveryBlock.com.

This is the core of an OpenBlock site, providing the web interface
that users see as well as the underlying data models. You need this.

For more information, see ebpub/README.TXT

ebdata
======

Code to help write scripts that import/crawl/parse data into ebpub.

You *will* need to write such scripts to get OpenBlock to do anything
useful; that is how you feed local news into the system.

For more information, see ebdata/README.TXT

obadmin
=======

Administrative UI, installation and utilities package for OpenBlock

==================
Other Packages
==================

ebblog
======

The blog application used by http://blog.everyblock.com

Only of interest if you want to bundle a simple blog with your
OpenBlock site; you can probably ignore this.

For more information, see ebblog/README.TXT



ebgeo
=====

The eb map system. This is mostly used for rendering and serving map
tiles with Mapnik. This package is optional and not installed by default.

For more information, see ebgeo/README.TXT


ebinternal
==========

Internal applications for the EveryBlock team.

Most OpenBlock users probably won't need this.
Not used by obdemo.

ebinternal consists of two apps, citypoll and feedback.  citypoll
powers EveryBlock's city voting system, both on EveryBlock.com and on
the iPhone app. feeback manages the feedback received from the
feedback forms at the bottom of almost every page on EveryBlock.com.

For more information, see ebinternal/README.TXT



ebwiki
======

A basic wiki.  

I'm not even sure if this is used on everyblock.com anymore.
Probably not useful to most OpenBlock users.

For more information, see ebwiki/README.TXT


everyblock
===========

This package contains code/templates that are specific to
EveryBlock.com. They were released to fulfill the terms of the grant
that funded EveryBlock's development and are likely not of general
use, with the possible exception of scraper scripts in
everyblock/cities/ and everyblock/states/ which may at least be useful
as examples of how to write scrapers.

For more information, see everyblock/README.TXT

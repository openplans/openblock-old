==========
everyblock
==========

This package contains code/templates that are specific to EveryBlock.com. They
are released to fulfill the terms of the grant that funded EveryBlock's
development and are likely not of general use.  However, the scrapers
provide a lot of good examples to emulate for writing scrapers, and
may be useful if you're targeting one of the covered cities/states.

Overview
========

The package is split into these directories:

    admin -- EveryBlock's internal admin application for managing its data

    cities -- City-specific data-acquisition scripts (for 15
    U.S. cities).  (Note that these do not currently include the
    necessary Schema definitions; you'd have to reverse-engineer those
    by looking at the attributes saved by each script, the schema
    slug, etc.  See ebpub/README.txt for more on Schema, Attributes,
    etc.)

    media -- CSS file for the admin

    states -- State-specific data-acquisition scripts

    staticmedia -- A Django template tag specific to EveryBlock.com media files

    templates -- Templates for the admin

    utils -- Various utilities used on EveryBlock.com


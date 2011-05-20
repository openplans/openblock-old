=========================
obdemo
=========================

The obdemo package contains code, templates, and configuration specific to
http://demo.openblockproject.org. 

They are intended to serve as a useful example of how to set up a site
based on the OpenBlock code.

By default, the site is set up to use Boston as the default location
for the maps.  You can change that by tweaking settings.py,
but then you're on your own for finding local data to load.

How The Demo Works
==================

obdemo uses the following parts of the OpenBlock codebase:

* :doc:`ebpub` does the heavy lifting, providing all the view and
  model code.  We also use the base templates, scripts, and css from
  here, although we override a few templates.

* :doc:`ebdata` is used to feed news data into the system.

* :doc:`obadmin` obadmin provides the administrative interface, the "oblock" 
  setup command that we use for installation and bootstrapping. It also provides
  a custom test runner (called as usual by ``manage.py test``).

* obdemo itself is a thin wrapper around the other packages and
  provides some data fixtures, migrations, and scripts to bootstrap
  the data used for the Boston demo.

For the maps, we use a free base layer based on Open Street Map and
hosted by OpenGeo.  Consequently, we don't need ebgeo_ or Mapnik.

We don't currently use any of the other openblock-extras_ packages
(ebblog, ebwiki, everyblock, or ebinternal).


Deployment
==========

For production deployment it's not generally recommended to run
``manage.py runserver``.  Most people use apache and mod_wsgi.

There's a suitable wsgi script at obdemo/wsgi/obdemo.wsgi.  It
assumes that you installed openblock in a virtualenv whose root
directory is the same as the checkout root; that's how the
bootstrap script sets things up.  If that's not true, you can copy
and modify the script and adjust the ``env_root`` variable.  If you used
the bootstrap script, it should just work.

For more information on configuring Apache and running Django apps
under mod_wsgi, see
http://docs.djangoproject.com/en/1.1/howto/deployment/modwsgi/

.. _ebgeo: https://github.com/openplans/openblock-extras/blob/master/docs/ebgeo.rst

.. _openblock-extras: https://github.com/openplans/openblock-extras/

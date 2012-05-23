==========
Deployment
==========


Apache
======

Most people use apache and mod_wsgi for deploying Django apps.
If you're deploying obdemo, there's a suitable wsgi script at
``obdemo/wsgi/obdemo.wsgi``; if you :doc:`generated a custom app
<../install/custom>`, there's a wsgi script at
``src/<projectname>/<projectname>/wsgi/<projectname>.wsgi``.

For more info, see
http://docs.djangoproject.com/en/1.3/howto/deployment/modwsgi/

Threading
=========

Be warned that GeoDjango in general - and thus OpenBlock -
is not safe to deploy multi-threaded. With mod_wsgi, this typically
means setting the ``threads=1`` option in the ``WSGIDaemonProcess`` directive.
See http://docs.djangoproject.com/en/1.3/ref/contrib/gis/deployment/
for more info.


Note on Virtual Hosting and Paths
=================================

Ensure that the user that openblock runs as has write permission
to the directory at settings.DJANGO_STATIC_SAVE_PREFIX.

Currently (2011/04/20), OpenBlock's views and templates (in the ebpub
package) contain a lot of hard-coded URLs that only work if the site
is deployed at the root of your domain.

In other words, you can deploy OpenBlock at http://example.com/ or
http://openblock.example.com/ but you can't successfully deploy it at
http://openexample.com/openblock.

.. _example_apache_config:

Example Apache Config
======================

Adjust the paths according to your installation.

.. code-block:: apacheconf


 <VirtualHost *:80>
 
 ServerName ....compute-1.amazonaws.com

 # Static media handling.
 # You'll want the "expires" module enabled.


 # Django admin static files; these may be under $VIRTUAL_ENV/lib/python2.x
 Alias /media/ /home/openblock/openblock/src/django/django/contrib/admin/media/
 Alias /static/media/ /home/openblock/openblock/src/django/django/contrib/admin/media/

 # You want aliases for all top-level subdirectories of ebpub/media
 Alias /styles/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/styles/
 Alias /scripts/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/scripts/
 Alias /images/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/images/
 Alias /cache-forever/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/cache-forever/
 Alias /olwidget/  /home/openblock/openblock/src/django-olwidget/

 # Only needed if you're running obdemo.
 Alias /map_icons/ /home/openblock/openblock/src/openblock/obdemo/obdemo/media/map_icons/

 <Directory /home/openblock/openblock/src/openblock/ebpub/ebpub/media/ >
   # I'm assuming everything here safely has a version-specific URL
   # whether via django-static or eg. the OpenLayers directory.
   ExpiresActive on
   ExpiresDefault "now plus 10 years"
 </Directory>
 
 WSGIScriptAlias / /home/openblock/openblock/src/openblock/obdemo/obdemo/wsgi/obdemo.wsgi
 WSGIDaemonProcess obdemo_org user=openblock group=www-data processes=10 threads=1
 WSGIProcessGroup obdemo_org
 
 CustomLog /var/log/apache2/openblock-access.log combined
 ErrorLog /var/log/apache2/openblock-error.log
 </VirtualHost>

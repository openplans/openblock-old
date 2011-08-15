==========
Deployment
==========


Apache
======

Most people use apache and mod_wsgi for deploying Django apps.
If you're deploying obdemo, there's a suitable wsgi script at
obdemo/wsgi/obdemo.wsgi.  Otherwise, see
http://docs.djangoproject.com/en/1.2/howto/deployment/modwsgi/

Threading
=========

Be warned that GeoDjango in general - and thus OpenBlock -
is not safe to deploy multi-threaded. With mod_wsgi, this typically
means setting the ``threads=1`` option in the ``WSGIDaemonProcess`` directive.
See https://docs.djangoproject.com/en/1.2/ref/contrib/gis/deployment/
for more info.


Note on Virtual Hosting and Paths
=================================

Currently (2011/04/20), OpenBlock's views and templates (in the ebpub
package) contain a lot of hard-coded URLs that only work if the site
is deployed at the root of your domain.

In other words, you can deploy OpenBlock at http://example.com/ or
http://openblock.example.com/ but you can't successfully deploy it at
http://openexample.com/openblock.

Example Apache Config
======================

Adjust the paths according to your installation.

.. code-block:: apacheconf


 <VirtualHost *:80>
 
 ServerName ....compute-1.amazonaws.com

 # Static media handling.
 # You'll want the "expires" module enabled.

 Alias /media/ /home/openblock/openblock/src/django/django/contrib/admin/media/
 Alias /styles/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/styles/
 Alias /scripts/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/scripts/
 Alias /images/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/images/
 Alias /cache-forever/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/cache-forever/
 
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

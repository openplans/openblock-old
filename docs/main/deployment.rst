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


Paths and Permissions
======================

Ensure that the user that openblock runs as has write permission to
the directories at settings.COMPRESS_OUTPUT_DIR and
settings.MEDIA_ROOT.
(For mod_wsgi, this is the user and/or group specified in the WSGIDaemonProcess line.

.. _example_apache_config:

Example Apache Config
======================

Adjust the paths according to your installation.

.. code-block:: apacheconf


 <VirtualHost *:80>
 
 ServerName ....compute-1.amazonaws.com

 # Static media handling.
 # You'll want the "expires" module enabled.

 # You want aliases for both MEDIA_ROOT at MEDIA_URL and STATIC_ROOT at STATIC_URL
 Alias /static/ /home/openblock/openblock/src/openblock/ebpub/ebpub/static_root/
 Alias /media/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media_root/

 <Directory /home/openblock/openblock/src/openblock/ebpub/ebpub/static_root/ >
   # I'm assuming everything here safely has a version-specific URL
   # whether via django-compressor or eg. the OpenLayers directory.
   ExpiresActive on
   ExpiresDefault "now plus 10 years"
 </Directory>
 <Directory /home/openblock/openblock/src/openblock/ebpub/ebpub/media_root/ >
   ExpiresActive on
   ExpiresDefault "now plus 10 years"
 </Directory>

 WSGIScriptAlias / /home/openblock/openblock/src/openblock/obdemo/obdemo/wsgi/obdemo.wsgi
 WSGIDaemonProcess obdemo_org display-name=obdemo_org user=openblock group=www-data processes=10 threads=1
 WSGIProcessGroup obdemo_org

 CustomLog /var/log/apache2/openblock-access.log combined
 ErrorLog /var/log/apache2/openblock-error.log
 </VirtualHost>

==========
Deployment
==========


Apache
======

Most people use apache and mod_wsgi for deploying Django apps.
If you're deploying obdemo, there's a suitable wsgi script at
obdemo/wsgi/obdemo.wsgi.  Otherwise, see
http://docs.djangoproject.com/en/1.1/howto/deployment/modwsgi/

Note on Virtual Hosting and Paths
---------------------------------

Currently (2011/04/20), OpenBlock's views and templates (in the ebpub
package) contain a lot of hard-coded URLs that only work if the site
is deployed at the root of your domain.

In other words, you can deploy OpenBlock at http://example.com/ or
http://openblock.example.com/ but you can't successfully deploy it at
http://openexample.com/openblock.

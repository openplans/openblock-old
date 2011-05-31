==================================
Running PostGIS on a remote server
==================================

If you're going to run postgresql on a separate server, you will still need to have postgres client libraries and development libraries installed on the machine which will be hosting the openblock software in order to connect and build the python postgres bindings.  On Ubuntu, for example, you can run:

.. code-block:: bash

   $ sudo apt-get install postgresql-client postgresql-server-dev-8.4

You or your database administrator should follow the instructions for :ref:`template_setup` and perform any database commands in the instructions such as `createuser`, `createdb`, and in general any steps performed as the postgres user on the database server.

You will need to work out any connection or authentication details with your database administrator.  Record the hostname, port, username and password used to connect to the database for use in Openblock's settings.

You will need to modify the DATABASES setting in your application to reflect these settings 
prior to running any django administrative commands.  Settings are located in the python 
package corresponding to the application, eg: myblock/myblock/settings.py or obdemo/obdemo/settings.py

See `Django's settings documentation
<https://docs.djangoproject.com/en/dev/topics/settings/>`_ and `Django's DATABASES setting documentation
<https://docs.djangoproject.com/en/dev/ref/settings/#databases>`_ for more information

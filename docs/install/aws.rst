=========================================
Installing OpenBlock on Amazon AWS
=========================================

This is the fastest way to try out OpenBlock.
You can launch an instance cloned from our AMI and start
feeding in data in minutes.

.. admonition:: Warning, experimental!

  Our AMI is still new and hasn't been widely tested. Please report
  any issue to the `mailing list <http://groups.google.com/group/ebcode/>`_.

Get an Account
==============

If you haven't registered for Amazon AWS, you might try out a
`free account <https://aws.amazon.com/free/>`_.
OpenBlock will happily run on the smallest (micro) EC2 instance size.

Launch an Instance ...
=======================

In the `AWS EC2 management console <https://console.aws.amazon.com/ec2/>`_,
click "Launch Instance". Click "Community AMIs", and in the search box, type in
"ami-e59b588c".  Select the OpenBlock AMI that comes up, then continue
through the wizard until your instance is launched. You can leave all
options at their default values (except the security group)
unless you know what you're doing.

.. admonition:: Security groups

  Note that the default security group has *all* ports closed.  You
  can modify your default security group, or create a new one; either
  way you *must* add the SSH and HTTP rules to open ports 22 and 80.
  Otherwise you won't be able to connect to your new instance at all.

As part of the setup, you'll be prompted to create a key pair.  It's
very important that you save the PEM file that it prompts you to
download.  You'll use this to ssh to your server later.

Or if you prefer, you can use Amazon's ``ec2-run-instances``
command-line tool, which is beyond the scope of this document.

Don't forget to stop it!
------------------------

Remember that AWS bills by the hour.  Especially if you're not on the
free plan, be sure to stop or terminate any instances you're not using
when done with them.

Does It Work?
=============

If all goes well, you will be immediately able to browse OpenBlock on
your new instance.  In the `AWS EC2 console <https://console.aws.amazon.com/ec2/>`_,
click on your running instance, and look for its "`Public DNS`".  This
will be a domain name such as
"ec2-50-17-54-xyz.compute-1.amazonaws.com".  Paste or type that into
your browser, and you should see the OpenBlock front page.

(Until you finish configuration and data loading, it'll have some
boring defaults, such as the title "OpenBlock: Your City", and there
will be no locations and no news.)


What You Have
=============

* Openblock 1.0.  The stable packages are installed in a virtualenv at
  `/home/openblock/openblock`.

* A "custom" app named "myblock" as per the :doc:`docs <custom>`,
  installed at `/home/openblock/openblock/src/myblock/myblock`

* Ubuntu 11.04 ("Natty"), Python 2.7, PostGIS, Apache2, mod_wsgi.

The code and its database are set up as if you had already followed
the :doc:`setup`, :doc:`base_install`, and :doc:`custom` instructions.

A few other nice details are taken care of for you:

* `django-background-tasks` is automatically started at boot via
  ``/etc/init.d/openblock-background-tasks``

* `updaterdaemon` is automatically started at boot via
  ``/etc/init.d/openblock-updaterdaemon``.

* ``logrotate`` is already configured to rotate the apache,
  django-background-task, and updaterdaemon logs, so they won't fill
  up your storage.

Get ssh access
===============

Next you'll need to log in to your server to do some configuration.
The username will be `openblock` and you'll need to use the PEM file
that you were prompted to save when you launched your instance,
and your public DNS that you can find in the EC2 console.

If you have a command-line `ssh` tool such as openssh, you can log in
like so:

.. code-block:: bash

 $ ssh -i <PATH TO YOUR PEM FILE> ubuntu@<YOUR PUBLIC DNS HERE>

If you're using another ssh tool such as PuTTY, try searching the web
for instructions on how to use it with AWS.


Once you're in...
=================

You'll be logged in as the `ubuntu` user, but openblock is installed
by the `openblock` user. So typically the first thing you will do is
run these commands:

.. code-block:: bash

 $ sudo su - openblock
 $ cd /home/openblock/openblock
 $ source bin/activate
 $ export DJANGO_SETTINGS_MODULE=myblock.settings


Change Settings
----------------

The OpenBlock config file will be at
``/home/openblock/openblock/src/myblock/myblock/settings.py``.
Edit that file as per :doc:`configuration`.

(Text editors `nano` and `vim` are installed; you can of course
install `emacs` or whatever else you like.)

**Security warning**: it is especially important that you change the
``PASSWORD_CREATE_SALT`` and ``PASSWORD_RESET_SALT`` settings.

Note that anytime you change settings, you'll want to run this command
before you can see your changes take effect on your site:

.. code-block:: bash

  $ sudo /etc/init.d/apache2 reload

(TODO, check if I enabled the "touch wsgi file" hack)

Make an Admin User
--------------------

Your instance does not come with an administrative django user,
because of course we don't want other people who clone the AMI to know
your password.  You can create one with this command:

.. code-block:: bash

 $ django-admin.py createsuperuser

Now you can log in at ``http://<your public DNS>/admin``.

What's Next
-------------

You'll want to start :doc:`geodata`.

Then you'll want to add some
:doc:`custom content types <../main/schemas>` to your site, and write some
:doc:`scraper scripts <../main/scraper_tutorial>` to populate them.

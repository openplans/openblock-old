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
"ami-f8ba1c91".  (You can also try searching for "openblock".)

If you can't find it, check your region; we publish AMIs in the
"us-east-1" region.  There is a dropdown to select region in the upper
left corner of the EC2 console.


Select the OpenBlock AMI, then continue
through the wizard until your instance is launched. You can leave all
options at their default values (except the security group)
unless you know what you're doing.

.. admonition:: Security groups

  Note that the default security group has *all* ports closed.  You
  can modify your default security group, or create a new one; either
  way you *must* add the SSH and HTTP rules to open ports 22 and 80.
  Otherwise you won't be able to connect to your new instance at all.

As part of the setup, you'll be prompted to create a key pair (if you
don't have one already).  It's very important that you save the PEM
file that it prompts you to download.  You'll use this to ssh to your
server later.

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

If the connection times out, make sure your security group allows
connecting to port 80.

Until you finish configuration and data loading, your site will have some
boring defaults, such as the title "OpenBlock: Your City", and there
will be no locations and no news.


What You Have
=============

* Openblock 1.2.  A checkout of the stable branch is installed in a virtualenv at
  `/home/openblock/openblock`.

* A "custom" app named "myblock" as per the :doc:`docs <custom>`,
  installed at ``/home/openblock/openblock/src/myblock/myblock``

* Ubuntu 12.04 ("Precise"), Python 2.7, Postgresql 9.1 and PostGIS 1.5, Apache2, mod_wsgi.

The code and its database are set up as if you had already followed
the :doc:`setup`, :doc:`base_install`, and :doc:`custom` instructions.

A few other nice details are taken care of for you:

* ``cron`` jobs are configured in ``/etc/cron.d/openblock``.
  Notably, this cron config has some commented-out examples of
  :doc:`running scraper scripts <../main/running_scrapers>`.
  It also periodically runs any :ref:`background_tasks`.
  It also sends the :doc:`alert <../main/alerts>` email messages.

* ``logrotate`` is already configured to rotate the apache and openblock
  logs, so they won't fill up your storage.

Get ssh access
===============

Next you'll need to log in to your server to do some configuration.
The username will be ``ubuntu`` and you'll need to use the PEM file
that you were prompted to save when you launched your instance,
and your public DNS that you can find in the EC2 console.

If you have a command-line ``ssh`` tool such as openssh, you can log in
like so:

.. code-block:: bash

 $ ssh -i <PATH TO YOUR PEM FILE> ubuntu@<YOUR PUBLIC DNS HERE>

If you're using another ssh tool such as PuTTY, try searching the web
for instructions on how to use it with AWS.


Once you're in...
=================

You'll be logged in as the ``ubuntu`` user, but openblock is installed
by the ``openblock`` user. So typically the first thing you will do is
run these commands:

.. code-block:: bash

 $ sudo su - openblock
 $ cd /home/openblock/openblock
 $ source bin/activate
 $ export DJANGO_SETTINGS_MODULE=myblock.settings

.. admonition:: Users and Permissions on Your EC2 Instance

  Note that the ``openblock`` user can do most anything that needs doing
  in its home directory, but has no password and has limited
  privileges beyond that, eg. cannot use ``sudo``.  I often keep a second
  terminal logged in as ``ubuntu`` for those times that I need to use
  ``sudo``.


Change Settings
----------------

The OpenBlock config file will be at
``/home/openblock/openblock/src/myblock/myblock/settings.py``.
Edit that file as per :doc:`configuration`.

(Text editors `nano` and `vim` are installed; you can of course
install `emacs` or whatever else you like.)

**Security warning**: it is *crucial* that you change the
``PASSWORD_CREATE_SALT`` and ``PASSWORD_RESET_SALT`` settings.
Otherwise, other people that create clones of the same AMI could
find the old salt values and try to crack your passwords.
You should also change ``STAFF_COOKIE_VALUE``.

Note that anytime you change settings, or update your openblock code,
you'll want to run this command
before you can see your changes take effect on your site:

.. code-block:: bash

  $  touch /home/openblock/openblock/wsgi/myblock.wsgi


.. admonition:: Warning about email!

  OpenBlock uses outgoing email for two features: account
  registration, and :doc:`email alert subscriptions <../main/alerts>`.
  **You can't really send email from an EC2 host.**
  Due to spam concerns, Amazon strictly limits the amount of email you
  can send, and many ISPs block email from EC2 anyway.
  The solution is to use another email server to send your outgoing
  email. If you don't have an SMTP server available, you may be able to use
  a gmail account or similar; for example, see `this blog post <http://www.mangoorange.com/2008/09/15/sending-email-via-gmail-in-django/>`_.
  Or you might try Amazon's own email service: https://aws.amazon.com/ses/

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

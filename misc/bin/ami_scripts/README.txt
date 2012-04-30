.. -*- mode: rst; -*-

==========================================
Building OpenBlock on Amazon EC2
==========================================

Scripts in here are for two purposes: creating a clone-able EC2 AMI,
or for smoke testing of the install docs on fresh Ubuntu images,
eg. on newly cloned EC2 AMIs.

The scripts should be literal translations of the instructions from
our docs.  I'm feeling out the approach, not sure yet if these are
worth keeping around, or what.  Chef or some such would be a more
robust alternative to a pile of ad-hoc shell scripts.

Creating Instances, Getting SSH Access
========================================

"Micro" EC2 instances are big enough, but "large" is much
faster for populating streets data.

I assume we're using Ubuntu AMI images. Get Ubuntu AMI numbers from here:
https://help.ubuntu.com/community/EC2StartersGuide#Official%20Ubuntu%20Amazon%20Machine%20Images%20%28AMIs%29
You want the EBS storage version, and I generally choose 64-bit.

If you install mr.awsome (http://pypi.python.org/pypi/mr.awsome)
locally, then there is an ``aws`` script and an ``etc/aws.conf``
config file that you can use to create, stop, terminate, etc. some
instances. Like so::

 $ aws start natty-64
 $ aws status natty-64
 $ aws terminate natty-64

Modify the config file as you like.
(You could also of course use Amazon's ec-* scripts but I find mr.awsome
convenient.)

To ssh to an EC2 instance, you get the public dns info from the AWS
control panel (or ``aws status``) and::

 $ export EC2HOST=ubuntu@....compute-1.amazonaws.com  # <-- your hostname goes here
 $ ssh -i ~/.ssh/openblock.pem $EC2HOST


Creating a Cloneable Image (AMI)
================================

First, set up an EC2 instance via eg.
``scenario_runner.sh $EC2HOST ubuntu1104 global dev custom.sh``

Then try the ``make_cloneable_image.sh <HOST>`` script.
This sets up apache, logrotate, cron jobs, openblock-related services.

Then you can use the EC2 management console (or scripts, if you like)
to create a clone-able AMI from this instance. 
On the web management console, this is as simple as:
* Select the instance
* Instance Actions -> Stop
* Instance Actions -> Create Image (EBS AMI)


Using EC2 for Release Testing - Manual
======================================

First create a new instance as described above.

Then run a specific base system setup script over ssh remotely like
so, substituting the hostname as needed::

 $ ssh -i ~/.ssh/openblock.pem $EC2HOST < src/openblock/ami_scripts/ubuntu1004_64_globalpkgs

Then set up the db with a specific db config::

 $ cat ubuntu1004_db_config db_postinstall | ssh -i ~/.ssh/openblock.pem $EC2HOST

Finally run a script to install openblock, eg.::

 $ ssh -i ~/.ssh/openblock.pem $EC2HOST < demo_setup_detailed.sh

Release Testing - More Automation
=====================================

There's now a little wrapper script that can do all that in one go.
The parameters are: hostname, distro version, global|local, dev|stable, install
script. Like so::

 $ /scenario_runner.sh ubuntu@$EC2HOST  ubuntu1004 local  dev demo_setup_detailed.sh


CONFIGURATIONS TO TEST:
=======================

platforms:

1. ubuntu 10.04 64 (lucid) (ami-63be790a)
2. ubuntu 10.10 64 (maverick) (ami-cef405a7)
3. ubuntu 11.04 64 (natty) (ami-fd589594)


sets of instructions:

1. demo_setup_quickstart.sh
2. demo_setup_detailed.sh
3. custom.rst

lib options:

1. gdal & lxml installed locally by pip (use *_globalpkgs)
2. gdal & lxml globally via distro packages (use *_noglobal)


XXX TODO: fix dry run:
south.exceptions.FailedDryRun:  ! Error found during dry run of '0007_auto__add_field_place_place_type'! Aborting.
Traceback (most recent call last):
  File "/home/openblock/openblock/lib/python2.6/site-packages/south/migration/migrators.py", line 175, in _run_migration
    migration_function()
  File "/home/openblock/openblock/lib/python2.6/site-packages/south/migration/migrators.py", line 57, in <lambda>
    return (lambda: direction(orm))
  File "/home/openblock/openblock/src/openblock/ebpub/ebpub/streets/migrations/0007_auto__add_field_place_place_type.py", line 10, in forwards
    default_place_type_id = orm['streets.PlaceType'].objects.get(slug='poi').id
  File "/home/openblock/openblock/lib/python2.6/site-packages/south/orm.py", line 395, in __getattr__
    raise AttributeError("You are in a dry run, and cannot access the ORM.\nWrap ORM sections in 'if not db.dry_run:', or if the whole migration is only a data migration, set no_dry_run = True on the Migration class.")
AttributeError: You are in a dry run, and cannot access the ORM.
Wrap ORM sections in 'if not db.dry_run:', or if the whole migration is only a data migration, set no_dry_run = True on the Migration class.


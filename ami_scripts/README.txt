.. -*- mode: rst; -*-

Scripts in here are intended just for testing install docs
remotely on fresh images, eg. on newly cloned EC2 AMIs.

The scripts should be literal translations of the instructions from
our docs.  I'm feeling out the approach, not sure yet if these are
worth keeping around, or what.

To ssh to an AMI you get the public dns info from the control panel and::
 $ ssh -i ~/.ssh/openblock.pem ubuntu@....compute-1.amazonaws.com

More likely we'll be using ssh to run scripts remotely.
First run a specific base system setup script over ssh remotely like
so, substituting the hostname as needed::

 $ ssh -i ~/.ssh/openblock.pem ubuntu@ec2-50-16-43-251.compute-1.amazonaws.com < src/openblock/ami_scripts/ubuntu1004_64_globalpkgs

Then set up the db with a specific db config::

 $ cat ubuntu1004_db_config db_postinstall | ssh -i ~/.ssh/openblock.pem ubuntu@ec2-50-16-43-251.compute-1.amazonaws.com

Finally run a script to install openblock, eg.::

 $ ssh -i ~/.ssh/openblock.pem ubuntu@ec2-50-16-43-251.compute-1.amazonaws.com < demo_setup_detailed.sh


There's now a little wrapper script that can do all that in one go.
The four parameters are: hostname, base setup script, db config file,
install script.  Like so::

 $ /scenario_runner.sh ec2-50-16-112-94.compute-1.amazonaws.com  ubuntu1004_64_globalpkgs  ubuntu1004_db_config demo_setup_detailed.sh

CONFIGURATIONS TO TEST:
=======================

platforms:

1. ubuntu 10.04 64 (ami-4abe4f23)
2. ubuntu 10.10 64 (ami-0843b561)
3. ubuntu 9.10 32  (ami-02b1406b)

instructions:

1. demo_setup.rst (quickstart)
2. demo_setup.rst (detailed)
3. custom.rst

lib options:

1. gdal & lxml installed locally by pip
2. gdal & lxml globally via distro packages

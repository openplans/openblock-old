.. -*- mode: rst; -*-

Scripts in here are intended just for testing install docs
remotely on fresh Ubuntu images, eg. on newly cloned EC2 AMIs.

The scripts should be literal translations of the instructions from
our docs.  I'm feeling out the approach, not sure yet if these are
worth keeping around, or what.

First create an EC2 instance (micro is big enough) from the
appropriate Ubuntu AMI. (Get the AMI numbers from here:
https://help.ubuntu.com/community/EC2StartersGuide#Official%20Ubuntu%20Amazon%20Machine%20Images%20%28AMIs%29
You want the EBS storage version, and I generally choose 64-bit.)

NOTE, if you install mr.awsome (http://pypi.python.org/pypi/mr.awsome)
there is an etc/aws.conf script that you can use to create, stop,
terminate, etc. some instances. Like so::

 $ aws start lucid-64

Modify the config file as you like.

To ssh to an EC2 instance, you get the public dns info from the AWS
control panel and::

 $ export EC2HOST=ubuntu@....compute-1.amazonaws.com  # <-- your hostname goes here
 $ ssh -i ~/.ssh/openblock.pem $EC2HOST

More likely we'll be using ssh to run scripts remotely.
First run a specific base system setup script over ssh remotely like
so, substituting the hostname as needed::

 $ ssh -i ~/.ssh/openblock.pem $EC2HOST < src/openblock/ami_scripts/ubuntu1004_64_globalpkgs

Then set up the db with a specific db config::

 $ cat ubuntu1004_db_config db_postinstall | ssh -i ~/.ssh/openblock.pem $EC2HOST

Finally run a script to install openblock, eg.::

 $ ssh -i ~/.ssh/openblock.pem $EC2HOST < demo_setup_detailed.sh


There's now a little wrapper script that can do all that in one go.
The four parameters are: hostname, base setup script, db config file,
install script.  Like so::

 $ /scenario_runner.sh $EC2HOST  ubuntu1004_64_globalpkgs  ubuntu1004_db_config demo_setup_detailed.sh

CONFIGURATIONS TO TEST:
=======================

platforms:

1. ubuntu 10.04 64 (lucid) (ami-63be790a)
2. ubuntu 10.10 64 (maverick) (ami-cef405a7)
3. ubuntu 11.04 64 (natty) (ami-1aad5273)


instructions:

1. demo_setup_quickstart.sh
2. demo_setup_detailed.sh
3. custom.rst  (TODO)

lib options:

1. gdal & lxml installed locally by pip (use *_globalpkgs)
2. gdal & lxml globally via distro packages (use *_noglobal)



Running on Port 80 via Apache
=============================

First run these commands:
$ sudo a2enmod expires
$ sudo apt-get install libapache2-mod-wsgi

Then try replacing /etc/apache2/sites-available/default with this
(inserting the ec2 instance's hostname on the ServerName line),
and then do `sudo /etc/init.d/apache2 reload` :


<VirtualHost *:80>


ServerName ....compute-1.amazonaws.com

Alias /media/ /home/openblock/openblock/src/django/django/contrib/admin/media/
Alias /styles/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/styles/
Alias /scripts/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/scripts/
Alias /images/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/images/
Alias /cache-forever/ /home/openblock/openblock/src/openblock/ebpub/ebpub/media/cache-forever/

<Directory /home/openblock/openblock/src/openblock/ebpub/ebpub/media/ >
  # I'm assuming everything here safely has a version-specific URL
  # whether via django-static or eg. the OpenLayers-2.9.1 directory.
  ExpiresActive on  
  ExpiresDefault "now plus 10 years"
</Directory>

WSGIScriptAlias / /home/openblock/openblock/src/openblock/obdemo/obdemo/wsgi/obdemo.wsgi

WSGIDaemonProcess obdemo_org user=openblock group=www-data processes=10 threads=1
WSGIProcessGroup obdemo_org

CustomLog /var/log/apache2/openblock-access.log combined
ErrorLog /var/log/apache2/openblock-error.log
</VirtualHost>


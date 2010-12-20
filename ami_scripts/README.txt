Scripts in here are intended just for testing install instructions
remotely on fresh images, eg. newly cloned EC2 AMIs.

ubuntu 10.04 AMI:  ami-1cdb2c75
micro size


To ssh in, get the public dns info from the control panel and:
$ ssh -i ~/.ssh/openblock.pem ubuntu@....compute-1.amazonaws.com

First run a specific scenario script over ssh remotely like so:
$ ssh -i ~/.ssh/openblock.pem ubuntu@ec2-50-16-43-251.compute-1.amazonaws.com < src/openblock/ami_scripts/ubuntu1004_64_globalpkgs

Then run this generic openblock installer script:
$ ssh -i ~/.ssh/openblock.pem ubuntu@ec2-50-16-43-251.compute-1.amazonaws.com < src/openblock/ami_scripts/ob_install.sh

... or maybe a different one for testing bootstrap_demo.sh?


CONFIGURATIONS TO TEST:
======================


platforms:
1. ubuntu 10.04 64
2. ubuntu 10.04 32


instructions:
1. setup.rst
2. demo_setup.rst
3. custom.rst

lib options:
1. gdal & lxml local
2. gdal & lxml global

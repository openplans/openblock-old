#!/bin/sh

# A tiny wrapper around obdemo/manage.py that makes sure your
# virtualenv is set up.  Symlink this into the root of the virtual env
# and run it from there.

cd `dirname $0`
. bin/activate
echo Setting up VIRTUAL_ENV $VIRTUAL_ENV
echo Running obdemo/obdemo/manage.py $@
obdemo/obdemo/manage.py $@


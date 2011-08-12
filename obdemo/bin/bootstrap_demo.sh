#!/bin/bash
#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#


# Quick experimental single-command script that does all the stuff 
# in ../../README.txt.

HARD_RESET=0
if [ "$1" == '-r' ]; then
    HARD_RESET=1
    shift
fi
# All other args will be passed to bootstrap.py

# Reliably and portably find the directory containing this script.
# Based roughly on stuff from:
# http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-in
HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD"/)`

# Find the root of our source checkout.
cd $HERE/../..
SOURCE_ROOT=$PWD
cd $OLDPWD

# Assume that $PWD is where you want the virtualenv.
# TODO: configurable?

echo Getting permission to run as postgres ...
sudo -u postgres echo ok || exit 1

# If we run this script in an already-activated virtualenv, the
# bootstrapper will blow up when attempting to copy the python binary
# on top of itself.  So, deactivate it.
# This is slightly tricky in a subshell:
if [ "$VIRTUAL_ENV" != "" ]; then
    source $VIRTUAL_ENV/bin/activate
    # If the old virtualenv is an old version with an old version of
    # setuptools (eg. 0.6c9) already installed in it, it's best to nuke that
    # because virtualenv won't upgrade it and it will cause a failure
    # like "... has no 'check_packages' attribute"; # see bug #118
    rm -rf $VIRTUAL_ENV/lib/python2.6/site-packages/setuptools* 2>/dev/null
    rm -rf $VIRTUAL_ENV/bin/easy_install* 2>/dev/null

    deactivate
    export PATH=`echo $PATH | sed -e "s|$VIRTUAL_ENV/bin:|:|"`
fi


echo Bootstrapping...
python $SOURCE_ROOT/bootstrap.py --distribute $@ || exit 1
source bin/activate || exit 1

if [ $HARD_RESET = 1 ]; then
    echo "Dropping openblock database(s)..."
    sudo -H -u postgres $VIRTUAL_ENV/bin/oblock drop_dbs || exit 1
    echo "Recreating database(s)..."
else
    echo "Creating database(s)..."
fi
sudo -H -u postgres bin/oblock setup_dbs  || exit 1


bin/oblock sync_all || exit 1

echo
echo =========================================================
echo Importing Boston geographic data...
export DJANGO_SETTINGS_MODULE=obdemo.settings
django-admin.py import_boston_zips || exit 1
django-admin.py import_boston_hoods || exit 1
# Note, it's important that blocks comes after zips.
django-admin.py import_boston_blocks || exit 1
echo
echo =========================================================
echo Importing Boston news...
django-admin.py import_boston_news || exit 1

echo 'Demo bootstrap succeeded!'
echo To start up the demo, try: django-admin.py runserver

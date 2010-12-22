#!/bin/bash

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

echo Importing Boston blocks...
export DJANGO_SETTINGS_MODULE=obdemo.settings
$HERE/import_boston_zips.sh || exit 1
$HERE/import_boston_hoods.sh || exit 1
$HERE/import_boston_blocks.sh || exit 1
$HERE/add_boston_news_schemas.sh || exit 1
$HERE/import_boston_news.sh || exit 1

echo 'Demo bootstrap succeeded!'
echo To start up the demo, try: $VIRTUAL_ENV/manage.py runserver

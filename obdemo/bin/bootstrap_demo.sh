#!/bin/bash

# Quick experimental single-command script that does all the stuff 
# in ../../README.txt.

if [ "$1" == '-r' ]; then
    HARD_RESET=1
fi

HERE=`dirname $0`
cd $HERE/../..

echo Getting permission to run as postgres ...
sudo -u postgres echo ok || exit 1

# Need this to be able to re-build the virtualenv
echo Removing old python binary...
rm -f bin/python

echo Bootstrapping...
# We want global packages because there's no easy way
# to get Mapnik installed locally.
python bootstrap.py --use-site-packages || exit 1
source bin/activate || exit 1

if [ $HARD_RESET = 1 ]; then
    echo "Dropping openblock database(s)..."
    sudo -u postgres bin/oblock drop_dbs || exit 1
    echo "Recreating database(s)..."
    sudo -u postgres bin/oblock setup_dbs  || exit 1
fi


bin/oblock sync_all || exit 1

echo Importing Boston blocks...
$HERE/import_boston_blocks.sh || exit 1
$HERE/add_boston_news_schemas.sh || exit 1
$HERE/import_boston_news.sh || exit 1

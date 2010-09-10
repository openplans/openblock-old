#!/bin/bash

# Quick experimental single-command script that does all the stuff 
# in ../../README.txt.

HERE=`dirname $0`
cd $HERE/../..

echo Getting permission to run as postgres ...
sudo -u postgres echo ok || exit 1

echo Dropping openblock DB...
sudo -u postgres dropdb openblock

echo Bootstrapping...
# We want global packages because there's no easy way
# to get Mapnik installed locally.
python bootstrap.py --use-site-packages=1 || exit 1
source bin/activate || exit 1

echo DB setup...
sudo -u postgres bin/oblock setup_dbs  || exit 1
bin/oblock sync_all || exit 1

echo Importing Boston blocks...
$HERE/import_boston_blocks.sh || exit 1
$HERE/add_boston_news_schemas.sh || exit 1
$HERE/import_boston_news.sh || exit 1

#!/bin/bash

HERE=`dirname $0`
cd $HERE/../..

echo Getting permission to run as postgres ...
sudo -u postgres test || exit 1

echo Dropping openblock DB...
dropdb openblock

echo Bootstrapping...
python bootstrap.py || exit 1
source bin/activate || exit 1

echo DB setup...
sudo -u postgres bin/paver setup_db  || exit 1
./manage.py syncdb || exit 1

echo Importing Boston blocks...
$HERE/import_boston_blocks.sh || exit 1

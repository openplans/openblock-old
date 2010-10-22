#!/bin/bash

SOURCE_ROOT=`dirname $0`
SOURCE_ROOT=`cd $SOURCE_ROOT/../.. && pwd`
echo Source root is $SOURCE_ROOT

export DJANGO_SETTINGS_MODULE=obdemo.settings

echo Set up news type schemas ...
cd $SOURCE_ROOT
echo in $PWD
./manage.py loaddata $SOURCE_ROOT/obdemo/obdemo/fixtures/boston_schemas.json


#!/bin/bash

export DJANGO_SETTINGS_MODULE=obdemo.settings

if [ ! -n "$VIRTUAL_ENV" ]; then
    echo Need to activate your virtualenv first.
    exit 1
fi

HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD"/)`
SOURCE_ROOT=`cd $HERE/../.. && pwd`
echo Source root is $SOURCE_ROOT


echo Set up news type schemas ...
cd $VIRTUAL_ENV
./manage.py loaddata $SOURCE_ROOT/obdemo/obdemo/fixtures/boston_schemas.json


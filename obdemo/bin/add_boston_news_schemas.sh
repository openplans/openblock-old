#!/bin/bash

if [ ! -n "$VIRTUAL_ENV" ]; then
    echo Need to activate your virtualenv first.
    exit 1
fi

if [ ! -n "$DJANGO_SETTINGS_MODULE" ]; then
    echo Please set DJANGO_SETTINGS_MODULE to your projects settings module
    exit 1
fi


HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD"/)`
SOURCE_ROOT=`cd $HERE/../.. && pwd`
echo Source root is $SOURCE_ROOT


echo Set up news type schemas ...
cd $VIRTUAL_ENV
django-admin.py loaddata $SOURCE_ROOT/obdemo/obdemo/fixtures/boston_schemas.json


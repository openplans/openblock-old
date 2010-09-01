#!/bin/bash

SOURCE_ROOT=`dirname $0`
SOURCE_ROOT=`cd $SOURCE_ROOT/../.. && pwd`
echo Source root is $SOURCE_ROOT

export DJANGO_SETTINGS_MODULE=obdemo.settings

function die {
    echo $@ >&2
    echo Exiting.
    exit 1
}

echo Adding latest events and news...
cd $SOURCE_ROOT/
./obdemo/bin/add_events.py || die
./obdemo/bin/add_news.py || die

echo Adding building permits...
python ./everyblock/everyblock/cities/boston/building_permits/retrieval.py || die


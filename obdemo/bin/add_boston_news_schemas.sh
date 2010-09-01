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

echo Set up news type schemas ...

cd $SOURCE_ROOT/misc/bin || die

echo events schema
./add_schema.py -f Event Events events "List of events in Boston" "Boston Events" "http://calendar.boston.com/" || die

echo news schema
./add_schema.py -f News News local-news "List of news in Boston" "Boston News" "http://www.cityofboston.gov/isd/building/asofright/default.asp" || die

echo Building Permits schema and SchemaField
./add_schema.py -f "Building Permit" "Building Permits" building-permits \
    "List of Boston Building Permits" "Boston Building Permits" \
    "http://www.cityofboston.gov/isd/building/asofright/default.asp" \
    raw_address varchar01 "Raw Address" "Raw Addresses" 1 0 0 0 1 1 \
    || die

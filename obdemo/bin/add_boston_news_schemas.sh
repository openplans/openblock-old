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
./add_schema.py -f News News local-news "List of news in Boston" "Boston News" "http://www.boston.com" || die

echo Building Permits schema and SchemaField
./add_schema.py -f "Building Permit" "Building Permits" building-permits \
    "List of Boston Building Permits" "Boston Building Permits" \
    "http://www.cityofboston.gov/isd/building/asofright/default.asp" \
    raw_address varchar01 "Raw Address" "Raw Addresses" 1 0 0 0 1 1 \
    || die
# TODO: how to add multiple SchemaFields?
#echo Businesses schema and SchemaField
#./add_schema.py -f "Business License" "Business Licenses" business-licenses \
#    "List of Boston Business Licenses" "Boston Business Licenses" \
#    "http://www.cityofboston.gov/cityclerk/search_reply.asp" \
#    ...
#    || die

#echo Boston city press releases
#./add_schema.py -f "Boston Press Release" "Boston Press Releases" city-press-releases \
#    "List of Boston City Press Releases" "Boston Press Releases" \
#    'http://www.cityofboston.gov/news/'
# TODO: schema fields

#echo Boston restaurant inspections
#./add_schema.py -f "Restaurant Inspection" "Restaurant Inspections" \
#    restaurant-inspections \
#    "List of Boston Restaurant Inspections" "Boston Restaurant Inspections" \
#    'http://www.cityofboston.gov/isd/health/mfc/search.asp'
# TODO: schema fields

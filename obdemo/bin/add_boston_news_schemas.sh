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

echo Adding events schema
./add_schema.py -f -n Event --description="List of events in Boston" \
  --summary="Boston Events" --source="http://calendar.boston.com/" || die

echo news schema
./add_schema.py -f -n News -s local-news \
  --description="List of news in Boston" \
  --summary="Boston News" --source="http://www.boston.com" || die

echo Building Permits schema and SchemaField
./add_schema.py -f -n "Building Permit" \
    --description="List of Boston Building Permits" \
    --summary="Boston Building Permits" \
    --source="http://www.cityofboston.gov/isd/building/asofright/default.asp" || die
./add_schemafield.py  -f -n raw_address -s building-permits -r varchar01 --pretty-name="Raw Address" --pretty-name-plural="Raw Addresses" --is-searchable

echo Adding SeeClickFix schema and schemafields
./add_schema.py -f -n "SeeClickFix Issue" -s issues \
    --description="List of Issues from SeeClickFix" \
    --summary="SeeClickFix Issues" --source="http://seeclickfix.com" || die

./add_schemafield.py  -f -n rating -s issues -r int01 \
    --pretty-name="Rating" --pretty-name-plural="Ratings" \
    --display || die


echo Boston Police Department news
./add_schema.py -f -n "Boston Police Department report" -s police-reports \
    --description="List of Boston Police Department reports" \
    --summary="Boston Police Department reports" \
    --source="http://www.bpdnews.com/feed/"

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

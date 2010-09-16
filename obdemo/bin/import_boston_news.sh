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

# TODO: give these a new schema, avoid duplicates, etc.
# not very useful till i do all that.
#echo Adding police reports...
#python obdemo/bin/bpdnews_retrieval.py || die

# more feeds from Joel. Local blog news:
./obdemo/bin/add_news.py "http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&scope=blogs&count=400&subject=massachusetts&format=atom"


echo Adding building permits...
python ./everyblock/everyblock/cities/boston/building_permits/retrieval.py || die

# TODO: fix traceback:  ebdata.blobs.scrapers.NoSeedYet: You need to add a Seed with the URL 'http://www.cityofboston.gov/news/
#echo Adding press releases...
#python everyblock/everyblock/cities/boston/city_press_releases/retrieval.py || die

# TODO: add attributes per retrieval.py.
#echo Adding restaurant inspections...
#python ./everyblock/everyblock/cities/boston/restaurants/retrieval.py || die

# TODO: separate schema for this
python obdemo/bin/seeclickfix_retrieval.py || die

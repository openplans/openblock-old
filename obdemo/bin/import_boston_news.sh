#!/bin/bash
#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#


HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD"/)`
SOURCE_ROOT=`cd $HERE/../.. && pwd`
echo Source root is $SOURCE_ROOT

function die {
    echo $@ >&2
    echo Exiting.
    exit 1
}

if [ ! -n "$DJANGO_SETTINGS_MODULE" ]; then
    die "Please set DJANGO_SETTINGS_MODULE to your projects settings module"
fi

echo Adding latest events and news...
cd $SOURCE_ROOT/obdemo/obdemo/scrapers
python add_events.py || die
python add_news.py || die
# more feeds from Joel. Local blog news:
python add_news.py "http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&scope=blogs&count=250&subject=massachusetts&format=atom"

echo Adding seeclickfix issues...
python seeclickfix_retrieval.py || die

echo Adding police reports...
python bpdnews_retrieval.py || die

echo Adding building permits...
cd $SOURCE_ROOT
python ./everyblock/everyblock/cities/boston/building_permits/retrieval.py || die

# TODO: fix traceback:  ebdata.blobs.scrapers.NoSeedYet: You need to add a Seed with the URL 'http://www.cityofboston.gov/news/
#echo Adding press releases...
#python everyblock/everyblock/cities/boston/city_press_releases/retrieval.py || die


cd $SOURCE_ROOT
echo Updating aggregates, see ebpub/README.txt...
python ebpub/ebpub/db/bin/update_aggregates.py

echo ___________________________________________________________________
echo
echo " *** NOT adding restaurant inspections, it may take hours. ***"
echo
echo "  If you want to load them, do:"
echo "  python $SOURCE_ROOT/everyblock/everyblock/cities/boston/restaurants/retrieval.py"
echo "  ... and then re-run python $SOURCE_ROOT/ebpub/ebpub/db/bin/update_aggregates.py"
echo ___________________________________________________________________


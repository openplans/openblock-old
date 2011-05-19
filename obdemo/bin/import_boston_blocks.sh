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


# Based on http://wiki.github.com/dkukral/everyblock/install-everyblock

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


# First we download a bunch of zipfiles of TIGER data.

BASEURL=http://www2.census.gov/geo/tiger/TIGER2009/25_MASSACHUSETTS
ZIPS="tl_2009_25_place.zip 25025_Suffolk_County/tl_2009_25025_edges.zip 25025_Suffolk_County/tl_2009_25025_faces.zip 25025_Suffolk_County/tl_2009_25025_featnames.zip"

mkdir -p tiger_data
cd tiger_data || die "couldn't cd to $PWD/tiger_data"

for fname in $ZIPS; do
    wget -N $BASEURL/$fname
    if [ $? -ne 0 ]; then
        die "Could not download $BASEURL/$fname"
    fi
done

for fname in *zip; do unzip -o $fname; done
echo Shapefiles unzipped in $PWD/tiger_data

# Now we load them into our blocks table.


IMPORTER=$SOURCE_ROOT/ebpub/ebpub/streets/blockimport/tiger/import_blocks.py
if [ ! -f "$IMPORTER" ]; then die "Could not find import_blocks.py at $IMPORTER" ; fi

echo Importing blocks, this may take several minutes ...

# Passing --city means we skip features labeled for other cities.
$IMPORTER  --city=BOSTON tl_2009_25025_edges.shp tl_2009_25025_featnames.dbf tl_2009_25025_faces.dbf tl_2009_25_place.shp || die

#########################

echo Populating streets and fixing addresses, these can take several minutes...

cd $SOURCE_ROOT/ebpub/ebpub/streets/bin || die

# Note these scripts should be run ONCE, in this order,
# after you have imported *all* your blocks.

./populate_streets.py -v -v -v -v streets || die
./populate_streets.py -v -v -v -v block_intersections || die
./populate_streets.py -v -v -v -v intersections || die

echo Done.

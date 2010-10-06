#!/bin/bash

# Based on http://wiki.github.com/dkukral/everyblock/install-everyblock

HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD"/)`
SOURCE_ROOT=`cd $HERE/../.. && pwd`
echo Source root is $SOURCE_ROOT

export DJANGO_SETTINGS_MODULE=obdemo.settings


function die {
    echo $@ >&2
    echo Exiting.
    exit 1
}


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

./populate_streets.py -v -v -v -v streets || die
./populate_streets.py -v -v -v -v block_intersections || die
./populate_streets.py -v -v -v -v intersections || die

echo Done.

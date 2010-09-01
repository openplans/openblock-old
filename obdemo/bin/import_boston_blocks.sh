#!/bin/bash

# Based on http://wiki.github.com/dkukral/everyblock/install-everyblock

SOURCE_ROOT=`dirname $0`
SOURCE_ROOT=`cd $SOURCE_ROOT/../.. && pwd`
echo Source root is $SOURCE_ROOT

export DJANGO_SETTINGS_MODULE=obdemo.settings


function die {
    echo $@ >&2
    echo Exiting.
    exit 1
}


rm -rf tiger_data
mkdir -p tiger_data
cd tiger_data || die "couldn't cd to $PWD/tiger_data"

# First we download a bunch of zipfiles of TIGER data.

BASEURL=http://www2.census.gov/geo/tiger/TIGER2009/25_MASSACHUSETTS
ZIPS="tl_2009_25_place.zip 25025_Suffolk_County/tl_2009_25025_edges.zip 25025_Suffolk_County/tl_2009_25025_faces.zip 25025_Suffolk_County/tl_2009_25025_featnames.zip"

for fname in $ZIPS; do
    wget $BASEURL/$fname
    if [ $? -ne 0 ]; then
        die "Could not download $BASEURL/$fname"
    fi
done

for fname in *zip; do unzip $fname; done
echo Shapefiles unzipped in $PWD/tiger_data

# Now we load them into our blocks table.


IMPORTER=`find -H $SOURCE_ROOT -name import_blocks.py`
if [ ! -f "$IMPORTER" ]; then die "Could not find import_blocks.py" ; fi

echo Importing blocks, this may take several minutes ...

$IMPORTER tl_2009_25025_edges.shp tl_2009_25025_featnames.dbf tl_2009_25025_faces.dbf tl_2009_25_place.shp || die

echo Creating a "'neighborhood'" location type...
cd $SOURCE_ROOT/misc/bin || die

./add_locationtype.py Neighborhood Neighborhoods neighborhoods neighborhoods || die

echo Importing neighborhoods, this may take a minute ...

cd $SOURCE_ROOT/misc/bin || die

./add_location.py "Beacon Hill" "Beacon Hill" beacon-hill neighborhoods Boston http://bostonneighborhoodmap.com/ "42.355282, -71.073530" "42.361259, -71.059794"

./add_location.py "West End" "West End" west-end neighborhoods Boston http://bostonneighborhoodmap.com/ "42.361543, -71.072498" "42.368279, -71.058504"

./add_location.py "North End" "North End" north-end neighborhoods Boston http://bostonneighborhoodmap.com/ "42.360009, -71.061507" "42.368826, -71.049185"

./add_location.py "Back Bay" "Back Bay" back-bay neighborhoods Boston http://bostonneighborhoodmap.com/ "42.345222, -71.091719" "42.35605, -71.070731"

./add_location.py "Bay Village" "Bay Village" bay-village neighborhoods Boston http://bostonneighborhoodmap.com/ "42.346678, -71.072421" "42.351023, -71.066612"

./add_location.py Charlestown Charlestown charleston neighborhoods Boston http://bostonneighborhoodmap.com/ "42.369953, -71.076024" "42.386476, -71.047983"

./add_location.py "East Boston" "East Boston" east-boston neighborhoods Boston http://bostonneighborhoodmap.com/ "42.349879, -71.043662" "42.397207, -71.985636"

./add_location.py "South Boston" "South Boston" south-boston neighborhoods Boston http://bostonneighborhoodmap.com/ "42.322102, -71.058578" "42.344339, -71.009413"

./add_location.py Waterfront Waterfront waterfront neighborhoods Boston http://bostonneighborhoodmap.com/ "42.338576, -71.054973" "42.354695, -71.023110"

./add_location.py "Fenway/Kenmore" "Fenway/Kenmore" fenway-kenmore neighborhoods Boston http://bostonneighborhoodmap.com/ "42.337880, -71.106093" "42.353080, -71.084205"

./add_location.py Downtown Downtown downtown neighborhoods Boston http://bostonneighborhoodmap.com/ "42.350701, -71.064736" "42.362947, -71.051308"

./add_location.py Chinatown Chinatown chinatown neighborhoods Boston http://bostonneighborhoodmap.com/ "42.347111, -71.066308" "42.352064, -71.053933"

./add_location.py "South End" "South End" south-end neighborhoods Boston http://bostonneighborhoodmap.com/ "42.332086, -71.087094" "42.348450, -71.058869"

./add_location.py "Mission Hill" "Mission Hill" mission-hill neighborhoods Boston http://bostonneighborhoodmap.com/ "42.326014, -71.112956" "42.342606, -71.092413"

./add_location.py "Jamaica Plain" "Jamaica Plain" jamaica-plain neighborhoods Boston http://bostonneighborhoodmap.com/ "42.296080, -71.131307" "42.326367, -71.099157"

./add_location.py Roxbury Roxbury roxbury neighborhoods Boston http://bostonneighborhoodmap.com/ "42.282421, -71.107001" "42.337916, -71.062619"

./add_location.py Mattapan Mattapan mattapan neighborhoods Boston http://bostonneighborhoodmap.com/ "42.260214, -71.115589" "42.292218, -71.067432"

./add_location.py Dorchester Dorchester dorchester neighborhoods Boston http://bostonneighborhoodmap.com/ "42.270124, -71.089461" "42.328234, -71.034102"

./add_location.py Allston Allston allston neighborhoods Boston http://bostonneighborhoodmap.com/ "42.338822, -71.143509" "42.372874, -71.113447"

./add_location.py Brighton Brighton brighton neighborhoods Boston http://bostonneighborhoodmap.com/ "42.335221, -71.172983" "42.364556, -71.144560"

./add_location.py "Hyde Park" "Hyde Park" hyde-park neighborhoods Boston http://bostonneighborhoodmap.com/ "42.230844, -71.14604" "42.277670, -71.110062"

./add_location.py "West Roxbury" "West Roxbury" west-roxbury neighborhoods Boston http://bostonneighborhoodmap.com/ "42.242338, -71.190201" "42.304530, -71.125352"

./add_location.py Roslindale Roslindale roslindale neighborhoods Boston http://bostonneighborhoodmap.com/ "42.270984, -71.146519" "42.296778, -71.106192"

echo Populating streets and fixing addresses...

cd $SOURCE_ROOT/ebpub/ebpub || die

./streets/fix_block_numbers.py || die
./streets/update_block_pretty_names.py || die
./streets/populate_streets.py streets || die
./streets/populate_streets.py block_intersections || die
./streets/populate_streets.py intersections || die

echo Done.

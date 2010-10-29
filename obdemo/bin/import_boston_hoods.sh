#!/bin/bash

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

HOOD_SERVER="http://developer.openblockproject.org/raw-attachment/ticket/62"
HOOD_FILE="Planning_districts_revised.zip" 
HOOD_URL="$HOOD_SERVER/$HOOD_FILE"
HOOD_FOLDER="$PWD/neighborhood_data"
HOOD_IMPORTER=$SOURCE_ROOT/ebpub/ebpub/db/bin/import_hoods.py

if [ ! -f "$HOOD_IMPORTER" ]; then
    die "Could not find import_hoods.py at $HOOD_IMPORTER"
fi


echo Downloading neighborhood data...

mkdir -p $HOOD_FOLDER
cd $HOOD_FOLDER || die "couldn't cd to $HOOD_FOLDER"

wget -N $HOOD_URL
if [ $? -ne 0 ]; then
    die "Could not download $HOOD_URL"
fi
unzip -o "$HOOD_FOLDER/$HOOD_FILE"

echo Importing neighborhoods...
$HOOD_IMPORTER -n PD $HOOD_FOLDER || die

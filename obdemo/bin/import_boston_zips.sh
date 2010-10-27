#!/bin/bash

HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD"/)`
SOURCE_ROOT=`cd $HERE/../.. && pwd`
echo Source root is $SOURCE_ROOT

export DJANGO_SETTINGS_MODULE=obdemo.settings


function die {
    echo $@ >&2
    echo Exiting.
    exit 1
}

ZIP_SERVER="http://developer.openblockproject.org/raw-attachment/ticket/62"
ZIP_FILE="bozip.zip" 
ZIP_URL="$ZIP_SERVER/$ZIP_FILE"
ZIP_FOLDER="$PWD/zip_data"
ZIP_IMPORTER=$SOURCE_ROOT/ebpub/ebpub/db/bin/import_zips.py

if [ ! -f "$ZIP_IMPORTER" ]; then die "Could not find import_zips.py at $ZIP_IMPORTER" ; fi

echo Downloading zip code data...

mkdir -p $ZIP_FOLDER
cd $ZIP_FOLDER || die "couldn't cd to $ZIP_FOLDER"

wget -N $ZIP_URL
if [ $? -ne 0 ]; then
    die "Could not download $ZIP_URL"
fi

unzip -o "$ZIP_FOLDER/$ZIP_FILE"

echo Importing zip codes...
$ZIP_IMPORTER $ZIP_FOLDER || die

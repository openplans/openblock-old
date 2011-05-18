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

unzip -o "$ZIP_FOLDER/$ZIP_FILE" || die "failed to unzip $ZIP_FOLDER/$ZIP_FILE"

echo Importing zip codes...
$ZIP_IMPORTER $ZIP_FOLDER || die

#!/bin/bash

# Script (hacky) to help with releasing a new version of the openblock packages.

HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD"/)`
SOURCE_ROOT=`cd $HERE/../.. && pwd`

export VERSION=$1

if [ -z "$VERSION" ]; then
    echo Need to specify the new version.
    exit 1
fi

cd $SOURCE_ROOT

for PKGDIR in ebpub ebdata obadmin obdemo; do
    cd $SOURCE_ROOT/$PKGDIR
    sed -i -e "s/VERSION=.*\$/VERSION=\"${VERSION}\"/" setup.py
    python setup.py sdist > /dev/null || exit 1
    FULLNAME=`python setup.py --fullname`
    echo -n "Does this status look right for $FULLNAME? "
    python setup.py --classifiers | grep -i status
    if [ -e dist/${FULLNAME}.tar.gz ]; then
	echo $FULLNAME package is at $PKGDIR/dist/${FULLNAME}.tar.gz
	echo
    else
	echo Failed to build $FULLNAME sdist. Try re-running python setup.py sdist to see why
    fi
done
cd $SOURCE_ROOT


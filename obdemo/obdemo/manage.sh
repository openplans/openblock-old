#!/bin/sh

# A tiny wrapper around obdemo/manage.py that makes sure your
# virtualenv is set up.  Symlink this into the root of the virtual env
# and run it from there.

cd `dirname $0`
. bin/activate
echo Setting up VIRTUAL_ENV $VIRTUAL_ENV

# locate the real location of this script
ORIG_LINK="$0"
TMP="$(readlink "$ORIG_LINK")"
while test -n "$TMP"; do
    ORIG_LINK="$TMP"
    TMP="$(readlink "$ORIG_LINK")"
done
MANAGE_PY=`dirname $ORIG_LINK`
MANAGE_PY="$MANAGE_PY/manage.py"

echo Running $MANAGE_PY $@
$MANAGE_PY $@


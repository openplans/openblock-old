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


# A tiny wrapper around manage.py that makes sure your
# virtualenv is set up.  Symlink this into the root of the virtual env
# and run it from there.

# Find the current directory where the symlink lives.
HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD")`
if [ "$VIRTUAL_ENV" != "$HERE" ]; then
    if [ -f $HERE/bin/activate ]; then
	source $HERE/bin/activate
    else
	echo "Can't find your virtualenv root."  1>&2
	echo $0 should be a symbolic link in the root of your virtualenv. 1>&2
	echo Check that. 1>&2
	exit 1
    fi
fi

# locate the real location of this script, no matter how many symlinks there are
ORIG_LINK="$0"
TMP=`readlink $ORIG_LINK`
while test -n "$TMP"; do
    ORIG_LINK="$TMP"
    TMP=`readlink "$ORIG_LINK"`
done

MANAGE_PY=`dirname $ORIG_LINK`/manage.py
$MANAGE_PY $@


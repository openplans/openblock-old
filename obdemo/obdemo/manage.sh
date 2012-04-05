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
# virtualenv is set up.
# Should work even if you run it via a symlink.

# locate the real location of this script, no matter how many symlinks there are
ORIG_LINK="$0"
TMP=`readlink $ORIG_LINK`
while test -n "$TMP"; do
    ORIG_LINK="$TMP"
    TMP=`readlink "$ORIG_LINK"`
done

HERE=`dirname $ORIG_LINK`
export HERE=`(cd "$HERE" 2>/dev/null; echo "$PWD"/)`

activator () 
{ 
    if [ "$VIRTUAL_ENV" != "" ]; then
        return;
    fi;

    ACTIVATOR_STARTDIR=$PWD;
    cd $HERE;
    unset ACTIVATOR_SCRIPT;

    while [ true ]; do
        if [ $PWD == '/' ]; then
            break;
        else
            if [ -f ./bin/activate ]; then
                ACTIVATOR_SCRIPT=$PWD/bin/activate;
                break;
            else
                if [ -f activate ]; then
                    ACTIVATOR_SCRIPT=$PWD/activate;
                    break;
                else
                    cd ..;
                fi;
            fi;
        fi;
    done;
    if [ -f "$ACTIVATOR_SCRIPT" ]; then
        source $ACTIVATOR_SCRIPT;
        if [ -d "$VIRTUAL_ENV" ]; then
            echo VIRTUAL_ENV is now $VIRTUAL_ENV;
        fi;
        cd $ACTIVATOR_STARTDIR;
        unset ACTIVATOR_SCRIPT ACTIVATOR_STARTDIR;
        return 0;
    else
        echo No activate script found.;
        cd $ACTIVATOR_STARTDIR;
        unset ACTIVATOR_SCRIPT ACTIVATOR_STARTDIR;
        return 1;
    fi
}

activator


MANAGE_PY=$HERE/manage.py
$MANAGE_PY $@


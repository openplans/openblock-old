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


if [ $# -ne 5 ]; then
    echo "Usage: `basename $0` remote-host version (local|global) (dev|stable) setup-script"
    echo
    echo Runs various scripts on remote-host.
    echo
    echo Example for ubuntu 10.10 with global system python packages on
    echo foo.amazonaws.com, with global \(apt-get\) installation of python C extensions,
    echo and openblock installed from stable packages, then running
    echo the \"demo_setup_detailed.sh\" scenario script:
    echo
    echo "  `basename $0` ubuntu@foo.amazonaws.com ubuntu1204 global stable demo_setup_detailed.sh"
    exit 1
fi

REMOTE=$1
VERSION=$2
LOCAL_OR_GLOBAL=$3
DEV_OR_STABLE=$4
SCENARIO_SCRIPT=$5

BASE_SCRIPT=${VERSION}_${LOCAL_OR_GLOBAL}pkgs
DB_CONFIG=${VERSION}_db_config

SSH="ssh -i $HOME/.ssh/openblock.pem"
echo ssh command is $SSH
echo

if [ ! -f "$BASE_SCRIPT" ]; then
    echo script "$BASE_SCRIPT" does not exist
    exit 1
else
    echo Will use $BASE_SCRIPT as base script
fi

if [ ! -f "$DB_CONFIG" ]; then
    echo script "$DB_CONFIG" does not exist
    exit 1
else
    echo Will use $DB_CONFIG as db config script
fi

if [ ! -f "$SCENARIO_SCRIPT" ]; then
    echo script "$SCENARIO_SCRIPT" does not exist
    exit 1
else
    echo Will use $SCENARIO_SCRIPT as scenario script
fi

echo Running $SSH $REMOTE '<' $BASE_SCRIPT...
$SSH $REMOTE < $BASE_SCRIPT || exit 1
echo OK
echo Waiting for it to come back up...
# Unfortunately EC2 servers don't seem to accept pinging.
while true; do
    sleep 4
    ssh -i ~/.ssh/openblock.pem $REMOTE "cat /etc/issue" && break
done

echo
echo Running SQL setup with $DB_CONFIG ...
cat $DB_CONFIG db_postinstall | $SSH $REMOTE  || exit 1
echo OK

if [ "$SCENARIO_SCRIPT" != "demo_setup_quickstart.sh" ]; then
    echo Preparing a virtualenv
    $SSH $REMOTE < base_install.sh || exit 1
    echo OK
    if [ "$LOCAL_OR_GLOBAL" == "local" ]; then
	echo Installing C extensions locally
	$SSH $REMOTE < localpkgs.sh || exit 1
	echo OK
    else
	echo C extensions should have been installed globally by $BASE_SCRIPT
    fi
    if [ "$DEV_OR_STABLE" == 'dev' ]; then
	echo Installing openblock from source...
	$SSH $REMOTE < ob_pkgs_from_source.sh || exit 1
	echo OK
    else
	echo Installing openblock from stable packages...
	$SSH $REMOTE < ob_pkgs_stable.sh || exit 1
	echo OK
    fi
fi

echo Running scenario $SCENARIO_SCRIPT...
$SSH $REMOTE < $SCENARIO_SCRIPT || exit 1
echo All OK



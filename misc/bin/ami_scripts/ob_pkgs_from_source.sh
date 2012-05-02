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

# Script that does everything after virtualenv setup, based on base_install.rst
# and demo_setup.rst.

export SUDO="sudo -H -E -u openblock"

# Speed up pip if we run again
export PIP_DOWNLOAD_CACHE=/home/openblock/pip-download-cache
export VIRTUAL_ENV=/home/openblock/openblock
echo Virtual env is in $VIRTUAL_ENV
cd $VIRTUAL_ENV || exit 1
export PIP=$VIRTUAL_ENV/bin/pip
echo
$SUDO mkdir -p src || exit 1

echo Cleaning up old source, if any...
$SUDO rm -rf src/openblock

echo Getting openblock source...

$SUDO git clone git://github.com/openplans/openblock.git src/openblock || exit 1
echo OK

BRANCH=openblock-1.2-branch
echo getting branch $BRANCH
cd src/openblock
$SUDO git checkout -b $BRANCH origin/$BRANCH || exit 1

echo
export SRC=$VIRTUAL_ENV/src/openblock
cd $SRC || exit 1
echo Installing openblock packages in `pwd`...

$SUDO $PIP install -r $SRC/ebpub/requirements.txt || exit 1
$SUDO $PIP install -e $SRC/ebpub || exit 1
$SUDO $PIP install -r $SRC/ebdata/requirements.txt || exit 1
$SUDO $PIP install -e $SRC/ebdata || exit 1
$SUDO $PIP install -r $SRC/obadmin/requirements.txt || exit 1
$SUDO $PIP install -e $SRC/obadmin || exit 1
$SUDO $PIP install -r $SRC/obdemo/requirements.txt || exit 1
$SUDO $PIP install -e $SRC/obdemo || exit 1
echo all packages installed

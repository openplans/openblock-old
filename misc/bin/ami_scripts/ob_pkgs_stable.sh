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
export PIP=$VIRTUAL_ENV/bin/pip
echo

#export REQ_URL=http://openplans.github.com/openblock/requirements/openblock-requirements-1.0.1.txt
export REQ_URL=http://slinkp.com/~paul/openblock/openblock-requirements-1.2rc1.txt

echo Installing dependencies from $REQ_URL
$SUDO $PIP install -r $REQ_URL || exit 1
## For testing not-yet-released packages:
## Filter out our own packages since for testing they may not be on pypi
#wget $REQ_URL -O - | egrep -v "ebpub|ebdata|obadmin|obdemo" > all-reqs.txt
#$SUDO $PIP install -r all-reqs.txt || exit 1
#$SUDO $PIP install http://slinkp.com/~paul/ebpub-1.0a2.tar.gz
#$SUDO $PIP install http://slinkp.com/~paul/ebdata-1.0a2.tar.gz
#$SUDO $PIP install http://slinkp.com/~paul/obadmin-1.0a2.tar.gz
#$SUDO $PIP install http://slinkp.com/~paul/obdemo-1.0a2.tar.gz


echo all packages installed


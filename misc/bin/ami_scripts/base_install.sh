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

# Script that does everything after database install, based on docs/setup.rst

# TODO: why not just run as the default user? why bother creating an
# openblock user? that's not in our docs.

# RESET user
echo Cleanup...
sudo rm -rf /home/openblock/openblock
sudo deluser openblock
echo setting up user
yes '' | sudo adduser --quiet --disabled-password openblock
echo
# END RESET

export SUDO="sudo -H -E -u openblock"

echo setting up virtualenv
cd /home/openblock
$SUDO virtualenv --system-site-packages openblock || $SUDO virtualenv openblock || exit 1
export VIRTUAL_ENV=$PWD/openblock
cd $VIRTUAL_ENV || exit 1

echo OK

# Can't just su to openblock and activate because that means
# there's no good way to deal with errors; exiting just means
# exiting out of the subshell.
#source bin/activate || exit 1

echo Upgrading pip and distribute...
$SUDO bin/easy_install --upgrade pip distribute || exit 1
$SUDO hash -r || echo "no hash"

echo OK

# Speed up pip if we run again
export PIP_DOWNLOAD_CACHE=/home/openblock/pip-download-cache

echo Virtual env is in $VIRTUAL_ENV
export PIP=$VIRTUAL_ENV/bin/pip


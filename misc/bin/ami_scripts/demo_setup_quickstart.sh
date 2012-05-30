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

# Script that does everything in docs/bootstrap.rst

# XXX We run as $USER, not using sudo explicitly, because the
# bootstrap script uses sudo and we need that to work.

# Speed up pip if we run again
export PIP_DOWNLOAD_CACHE=$HOME/pip-download-cache
cd $HOME
rm -rf openblock
mkdir -p openblock/src || exit 1
cd openblock || exit 1
git clone git://github.com/openplans/openblock.git src/openblock || exit 1

BRANCH=openblock-1.2-branch
cd src/openblock
git checkout $BRANCH
cd -

echo
echo Bootstrapping...

src/openblock/obdemo/bin/bootstrap_demo.sh -r || exit 1

echo Testing...
DJANGO_SETTINGS_MODULE=obdemo.settings bin/django-admin.py test db openblockapi

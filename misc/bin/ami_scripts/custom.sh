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
# and custom.rst.

export SUDO="sudo -H -E -u openblock"

export VIRTUAL_ENV=/home/openblock/openblock
cd $VIRTUAL_ENV || exit 1
source bin/activate || exit 1

$SUDO mkdir -p src
cd src || exit 1

echo Creating project from paster template
$SUDO $VIRTUAL_ENV/bin/paster create --no-interactive -t openblock myblock || exit 1
echo OK

echo Installing myblock package...
cd myblock
$SUDO $VIRTUAL_ENV/bin/python setup.py develop || exit 1
echo OK

echo Creating DB...
sudo -u postgres dropdb openblock_myblock 2> /dev/null
sudo -u postgres createdb -U openblock --template template_postgis openblock_myblock || exit 1
echo OK

echo Syncing DB...
DJADMIN="$SUDO env DJANGO_SETTINGS_MODULE=myblock.settings $VIRTUAL_ENV/bin/django-admin.py"
# Skip creating superuser.
$DJADMIN syncdb --noinput --migrate || exit 1
echo OK

echo Testing...
$DJADMIN test db openblockapi

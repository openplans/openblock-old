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

export VIRTUAL_ENV=/home/openblock/openblock
cd $VIRTUAL_ENV || exit 1
source bin/activate

echo Setting up obdemo config file

OBDEMO_DIR=`python -c "import obdemo, os; print os.path.dirname(obdemo.__file__)"`
cd $OBDEMO_DIR || exit 1

echo Randomizing salts and cookies
$SUDO $VIRTUAL_ENV/bin/python - <<EOPYTHON
import string, random
text = open('settings.py.in', 'r').read()
out = open('settings.py', 'w')
while text.count('REPLACE_ME'):
    text = text.replace(
        '<REPLACE_ME>',
        ''.join([random.choice(string.letters + string.digits) for i in range(25)]),
        1)
out.write(text)
out.close()

EOPYTHON

cd -
echo OK
echo

echo Setting up DBs

sudo -u postgres dropdb openblock 2> /dev/null
sudo -u postgres createdb -U openblock --template template_postgis openblock || exit 1

echo Syncing DB...

DJADMIN="$SUDO env DJANGO_SETTINGS_MODULE=obdemo.settings $VIRTUAL_ENV/bin/django-admin.py"
# Skip creating superuser.
$DJADMIN syncdb --noinput --migrate || exit 1
echo OK

echo Importing demo data...
$DJADMIN import_boston_zips || exit 1
$DJADMIN import_boston_hoods || exit 1
$DJADMIN import_boston_blocks || exit 1
# Not exiting here because any random news source site being down can give spurious failures.
$DJADMIN import_boston_news

echo Testing...
$DJADMIN test db openblockapi

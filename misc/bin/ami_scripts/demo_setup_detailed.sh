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

# XXX RESET DB and user
echo Cleanup...
sudo -u postgres dropdb openblock
sudo -u postgres dropuser openblock
sudo rm -rf /home/openblock/openblock
sudo deluser openblock
# XXX END RESET


echo setting up user
yes '' | sudo adduser --quiet --disabled-password openblock
echo

export SUDO="sudo -H -E -u openblock"

echo setting up virtualenv
cd /home/openblock
$SUDO virtualenv openblock || exit 1
export VIRTUAL_ENV=$PWD/openblock
cd openblock || exit 1

echo

# Can't just su to openblock and activate because that means
# there's no good way to deal with errors; exiting just means
# exiting out of the subshell.
#source bin/activate || exit 1

$SUDO bin/easy_install --upgrade pip distribute || exit 1
$SUDO hash -r

# Speed up pip if we run again
export PIP_DOWNLOAD_CACHE=/home/openblock/pip-download-cache

echo Virtual env is in $VIRTUAL_ENV
export PIP=$VIRTUAL_ENV/bin/pip
echo

# TODO: Ugh. We should explicitly install lxml and gdal only
# if explicitly told to do so
echo installing lxml if not installed...
bin/python -c "import lxml" 2>/dev/null
if [ $? != 0 ]; then
    echo lxml not installed, trying to install it locally
    $SUDO $PIP install -v lxml || exit 1
    echo OK
fi
bin/python -c "import lxml" || exit 1
echo lxml OK
echo

# Ugh ugh ugh.
echo installing GDAL if not installed...
bin/python -c "import gdal" 2>/dev/null
if [ $? != 0 ]; then
    echo "GDAL (for python) not installed, trying to install it locally"
    gdal-config --version || exit 1
    GDAL_MAJOR_VERSION=`gdal-config --version | cut -d '.' -f 1,2`
    $SUDO $PIP install --no-install "GDAL>=$GDAL_MAJOR_VERSION,<=$GDAL_MAJOR_VERSION.9999" || exit 1
    cd build/GDAL || exit 1
    $SUDO rm -f setup.cfg
    GDAL_LIBDIRS=`gdal-config --libs | sed -r -e 's/-[^L]\S*//g' -e 's/\s*-L//g'`
    GDAL_LIBS=`gdal-config --libs | sed -r -e 's/-[^l]\S*//g' -e 's/\s*-l//g'`
    GDAL_INCDIRS=`gdal-config --cflags | sed -r -e 's/-[^I]\S*//g' -e 's/\s*-I//g'`
    $SUDO $VIRTUAL_ENV/bin/python setup.py build_ext --gdal-config=gdal-config \
      --library-dirs="$GDAL_LIBDIRS" \
      --libraries="$GDAL_LIBS" \
      --include-dirs="$GDAL_INCDIRS" \
    install || exit 1
fi

cd $VIRTUAL_ENV
bin/python -c "import gdal" || exit 1

echo Getting openblock source...
$SUDO mkdir -p src/ || exit 1
$SUDO git clone git://github.com/openplans/openblock.git src/openblock || exit 1

echo
echo Installing openblock packages in `pwd`...
cd $VIRTUAL_ENV/src/openblock || exit 1


SRC=$VIRTUAL_ENV/src/openblock
$SUDO $PIP install -r $SRC/ebpub/requirements.txt
$SUDO $PIP install -e $SRC/ebpub
$SUDO $PIP install -r $SRC/ebdata/requirements.txt
$SUDO $PIP install -e $SRC/ebdata
$SUDO $PIP install -r $SRC/obadmin/requirements.txt
$SUDO $PIP install -e $SRC/obadmin
$SUDO $PIP install -r $SRC/obdemo/requirements.txt
$SUDO $PIP install -e $SRC/obdemo
echo all packages installed

echo Setting up obdemo config file
cd $VIRTUAL_ENV/src/openblock/obdemo/obdemo || exit 1
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

echo OK
echo

echo Creating db user
sudo -u postgres createuser --no-superuser --inherit --createrole --createdb openblock || exit 1
echo Creating db
sudo -u postgres createdb -U openblock --template template_postgis openblock || exit 1

echo Setting up DBs

cd $VIRTUAL_ENV/src/openblock/obdemo/obdemo
echo Syncing DB...

DJADMIN="$SUDO env DJANGO_SETTINGS_MODULE=obdemo.settings django-admin.py"
yes no | $DJADMIN syncdb --migrate || exit 1
echo OK

$DJADMIN import_boston_zips || exit 1
$DJADMIN import_boston_hoods || exit 1
$DJADMIN import_boston_blocks || exit 1
$DJADMIN import_boston_news || exit 1



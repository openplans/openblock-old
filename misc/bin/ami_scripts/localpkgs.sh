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

cd $VIRTUAL_ENV
source bin/activate

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

echo installing GDAL if not installed...
bin/python -c "import gdal" 2>/dev/null
if [ $? != 0 ]; then
    echo "GDAL (for python) not installed, trying to install it locally"
    gdal-config --version || exit 1
    GDAL_MAJOR_VERSION=`gdal-config --version | cut -d '.' -f 1,2`
    $SUDO $PIP install --no-install "GDAL>=$GDAL_MAJOR_VERSION,<=$GDAL_MAJOR_VERSION.9999" || exit 1
    # Workaround for building gdal with missing header; needed at least on ubuntu 12.04
    if [ ! -f /usr/include/gdal/swq.h ]; then
        cd /usr/include/gdal
        sudo wget http://svn.osgeo.org/gdal/branches/$GDAL_MAJOR_VERSION/gdal/ogr/swq.h
        cd -
    fi
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

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

$SUDO bin/easy_install pip || exit 1

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

# XXX using branch for now
cd src/openblock || exit 1
$SUDO git fetch origin docs-redo:docs-redo || exit 1
$SUDO git checkout docs-redo || exit 1
# end XXX

echo
echo Installing openblock packages in `pwd`...
cd $VIRTUAL_ENV/src/openblock || exit 1


$SUDO $PIP install -r ebpub/requirements.txt -e ebpub || exit 1
$SUDO $PIP install -r ebdata/requirements.txt -e ebdata  || exit 1
$SUDO $PIP install -r obadmin/requirements.txt -e obadmin || exit 1
$SUDO $PIP install -r obdemo/requirements.txt -e obdemo || exit 1
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
#sudo su - openblock || exit 1
#echo I am now `whoami`
#cd /home/openblock/openblock
#source bin/activate

cd $VIRTUAL_ENV/src/openblock/obdemo/obdemo
echo Syncing DB...

# Have to do these in the right order.
yes no | $SUDO $VIRTUAL_ENV/bin/python ./manage.py syncdb --database=users || exit 1
$SUDO $VIRTUAL_ENV/bin/python ./manage.py syncdb --database=metros || exit 1
$SUDO $VIRTUAL_ENV/bin/python ./manage.py syncdb --database=default || exit 1
# The stupid workardound for geo columns not existing when custom sql gets run.
$SUDO $VIRTUAL_ENV/bin/python ./manage.py dbshell --database=default < ../../ebpub/ebpub/db/sql/location.sql || exit 1
echo OK

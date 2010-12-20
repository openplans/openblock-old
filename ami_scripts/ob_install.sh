# XXX RESET
echo Cleanup...
sudo -u postgres dropdb openblock
sudo -u postgres dropuser openblock
sudo rm -rf /home/openblock/openblock
sudo deluser openblock
# XXX END RESET

export SUDO="sudo -H -E -u openblock"
echo setting up user
yes '' | sudo adduser --quiet --disabled-password openblock
echo
echo setting up virtualenv
cd /home/openblock
$SUDO virtualenv openblock || exit 1
export VIRTUAL_ENV=$PWD/openblock
cd openblock || exit 1

# Can't just su to openblock and activate because that means
# there's no good way to deal with errors; exiting just means
# exiting out of the subshell.
#source bin/activate || exit 1

$SUDO bin/easy_install pip || exit 1
# XXX Speed up pip if we run again
export PIP_DOWNLOAD_CACHE=/home/openblock/pip-download-cache

echo Virtual env is in $VIRTUAL_ENV
export PIP=$VIRTUAL_ENV/bin/pip
echo
# we should've already installed it, just verifying.
bin/python -c "import lxml" || exit 1
echo lxml OK
echo
echo Getting openblock source...
$SUDO mkdir -p src/ || exit 1
$SUDO git clone git://github.com/openplans/openblock.git src/openblock || exit 1

# XXX using branch for now
cd src/openblock || exit 1
$SUDO git checkout docs-redo || exit 1
# end XXX

echo
echo Installing openblock packages in `pwd`...
cd $VIRTUAL_ENV/src/openblock || exit 1
# XXX TODO: we have several ways to install gdal that we need to try.
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
echo OK

# Script that does everything in docs/setup_demo.rst#quickstart

# XXX We run as $USER, not using sudo explicitly, because the
# bootstrap script uses sudo and we need that to work.

# Speed up pip if we run again
export PIP_DOWNLOAD_CACHE=/home/openblock/pip-download-cache
cd $HOME
rm -rf openblock
mkdir -p openblock/src || exit 1
cd openblock || exit 1
git clone git://github.com/openplans/openblock.git src/openblock || exit 1
# XXX using branch for now
cd src/openblock || exit 1
git fetch origin docs-redo:docs-redo || exit 1
git checkout docs-redo || exit 1
cd -
# end XXX

echo
echo Bootstrapping...

src/openblock/obdemo/bin/bootstrap_demo.sh -r || exit 1


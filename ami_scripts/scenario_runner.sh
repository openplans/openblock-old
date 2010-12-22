#!/bin/bash

if [ $# -ne 4 ]; then
    echo Usage: `basename $0` remote-host base-script db-config setup-script
    echo
    echo Runs base-script on remote-host, then sets up postgis on remote-host
    echo using db-config to find postgis files,
    echo then runs the setup-script on remote-host.
    echo
    echo Example for ubuntu 10.10 with global system python packages on
    echo foo.amazonaws.com, with openblock installed via setup_rst.sh :
    echo
    echo "  `basename $0` foo.amazonaws.com ubuntu1010_64_globalpkgs ubuntu1010_db_config setup_rst.sh"
    exit 1
fi

REMOTE=$1
BASE_SCRIPT=$2
DB_CONFIG=$3
SETUP_SCRIPT=$4

SSH="ssh -i $HOME/.ssh/openblock.pem"
echo Running base script $BASE_SCRIPT...
$SSH ubuntu@$REMOTE < $BASE_SCRIPT || exit 1
echo OK
#echo Waiting for it to come back up...
#sleep 20
# Unfortunately EC2 servers don't seem to accept pinging.
echo
echo Running SQL setup with $DB_CONFIG ...
cat $DB_CONFIG db_postinstall | $SSH ubuntu@$REMOTE  || exit 1
echo OK

echo Running scenario $SCENARIO_SCRIPT...
$SSH ubuntu@$REMOTE < $SETUP_SCRIPT || exit 1
echo All OK



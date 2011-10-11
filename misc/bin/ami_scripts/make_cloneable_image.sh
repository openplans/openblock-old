#!/bin/sh

# After bootstrapping an image with scenario_runner.sh,
# run this to make something we can clone an AMI from.

REMOTE="$1"
export SSH="ssh -i $HOME/.ssh/openblock.pem"
export RSYNC_RSH="$SSH"

echo Installing apache modules
$SSH $REMOTE <<EOF
    sudo a2enmod expires
    sudo apt-get -y install libapache2-mod-wsgi logrotate
    mkdir -p /tmp/stuff/
EOF


echo Copying files
DIR=etc/base_image_files

rsync -auv $DIR/* $REMOTE:/tmp/stuff/ || exit 1
echo OK

echo Putting files in place...
$SSH $REMOTE <<EOF
    sudo rsync -av /tmp/stuff/ /
    sudo rm -f /home/openblock/openblock/wsgi
    sudo ln -s /home/openblock/openblock/src/myblock/myblock/wsgi /home/openblock/openblock/wsgi
    echo Restarting apache...
    sudo /etc/init.d/apache2 restart
    echo Restarting cron...
    sudo service cron restart
    echo Adding services...
    sudo update-rc.d openblock-updaterdaemon defaults
    sudo update-rc.d openblock-background-tasks defaults

EOF
echo OK


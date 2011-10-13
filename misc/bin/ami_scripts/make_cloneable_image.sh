#!/bin/sh

# After bootstrapping an image with scenario_runner.sh,
# run this to make something we can clone an AMI from.

REMOTE="$1"
export SSH="ssh -i $HOME/.ssh/openblock.pem"
export RSYNC_RSH="$SSH"

echo Installing apache modules
$SSH $REMOTE <<EOF
    sudo apt-get -y install libapache2-mod-wsgi logrotate
    sudo a2enmod expires
    sudo rm -rf /tmp/stuff/
    mkdir -p /tmp/stuff/
EOF


echo Copying files
DIR=etc/base_image_files

rsync -auv $DIR/* $REMOTE:/tmp/stuff/ || exit 1
echo OK

echo Putting files in place...
$SSH $REMOTE <<EOF
    sudo rsync -av /tmp/stuff/ /
    # fix ownership we just clobbered
    sudo chown -R openblock /home/openblock
    sudo chown root.root /etc/cron.d/openblock

    sudo rm -f /home/openblock/openblock/wsgi
    sudo ln -s /home/openblock/openblock/src/myblock/myblock/wsgi /home/openblock/openblock/wsgi
    echo Restarting apache...
    sudo /etc/init.d/apache2 restart
    echo Restarting cron...
    sudo service cron restart
EOF
echo OK


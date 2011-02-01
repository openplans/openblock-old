#!/bin/bash
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


if [ ! -n "$VIRTUAL_ENV" ]; then
    echo Need to activate your virtualenv first.
    exit 1
fi

if [ ! -n "$DJANGO_SETTINGS_MODULE" ]; then
    echo Please set DJANGO_SETTINGS_MODULE to your projects settings module
    exit 1
fi


HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD"/)`
SOURCE_ROOT=`cd $HERE/../.. && pwd`
echo Source root is $SOURCE_ROOT


echo Set up news type schemas ...
cd $VIRTUAL_ENV
django-admin.py loaddata $SOURCE_ROOT/obdemo/obdemo/fixtures/boston_schemas.json


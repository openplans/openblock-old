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


# Updates restaurants (very very slow scraper), while periodicially
# updating aggregates too.

python $VIRTUAL_ENV/src/openblock/ebdata/ebdata/scrapers/us/ma/boston/restaurants/retrieval.py &
RESTAURANTS_PID=$!
echo RESTAURANTS_PID=$RESTAURANTS_PID
while true; do
	echo updating aggregates again...
	python $VIRTUAL_ENV/src/openblock/ebpub/ebpub/db/bin/update_aggregates.py
	ps | grep $RESTAURANTS_PID || break
	sleep 300 
done

echo Done updating aggregates...
wait $RESTAURANTS_PID

echo Done.

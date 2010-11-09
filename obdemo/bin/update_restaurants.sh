#!/bin/bash

# Updates restaurants (very very slow scraper), while periodicially
# updating aggregates too.

python $VIRTUAL_ENV/src/openblock/everyblock/everyblock/cities/boston/restaurants/retrieval.py &
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

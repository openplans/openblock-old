#!/usr/bin/env python
# encoding: utf-8

import datetime
import random
import sys
import uuid

import os
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'obdemo.settings'

from ebpub.db.models import NewsItem, Schema
from ebpub.db.models import Location

def main(count):
    schema = 'local-news'

    locations = list(Location.objects.all())
    random.shuffle(locations)

    try:
        schema = Schema.objects.get(slug=schema)
    except Schema.DoesNotExist:
        print "Schema (%s): DoesNotExist" % schema
        sys.exit(0)
        
    for i in range(int(count)):
        item = NewsItem()
        item.schema = schema
        item.title = '%d Random News %s' % (i, uuid.uuid1())
        item.description = item.title + ' blah' * 100
        item.url = 'http://example.com'
        # Random time between now and one week ago.
        date = datetime.datetime.now() - datetime.timedelta(random.uniform(-7.0, 0.0))
        item.pub_date = item.item_date = date

        # Pick a random location from the ones we know.
        location = locations[i % len(locations)]
        item.location_object = location
        item.location_name = location.name
        # It would be cool to pick a random location within the bounds,
        # but that would take thought... use the center.
        try:
            item.location = location.location.centroid
        except AttributeError:
            print "whoops"
            continue
        print "Added: %s at %s (%s)" % (item.title, location.name, item.location.wkt)
        item.save()


    
if __name__ == '__main__':
    try:
        count = sys.argv[1]
    except IndexError:
        sys.stderr.write("Usage: %s N\n" % sys.argv[0])
        sys.stderr.write("Generates N randomly-placed articles.\n")
        sys.exit(1)
    sys.exit(main(count))

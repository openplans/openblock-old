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
from ebpub.streets.models import Block

def main(count):
    schema = 'local-news'


    try:
        schema = Schema.objects.get(slug=schema)
    except Schema.DoesNotExist:
        print "Schema (%s): DoesNotExist" % schema
        sys.exit(1)
    last_block_id = Block.objects.order_by('-id')[0].id

    for i in range(int(count)):
        item = NewsItem()
        item.schema = schema
        item.title = '%d Random News %s' % (i, uuid.uuid4())
        item.description = item.title + ' blah' * 100
        item.url = 'http://example.com'
        # Random time between now and one week ago.
        date = datetime.datetime.now() - datetime.timedelta(random.uniform(-7.0, 0.0))
        item.pub_date = item.item_date = date

        # Pick a random block.
        while True:
            block_id = random.randint(1, last_block_id)
            try:
                block = Block.objects.get(id=block_id)
                break
            except Block.objects.DoesNotExist:
                continue

        item.location_name = block.pretty_name
        item.block = block
        try:
            item.location = block.geom.centroid
        except AttributeError:
            item.location = block.geom

        print "Added: %s at %s (%s)" % (item.title, item.location_name, item.location.wkt)
        item.save()


    
if __name__ == '__main__':
    try:
        count = sys.argv[1]
    except IndexError:
        sys.stderr.write("Usage: %s N\n" % sys.argv[0])
        sys.stderr.write("Generates N randomly-placed articles.\n")
        sys.exit(1)
    sys.exit(main(count))

#!/usr/bin/env python
# encoding: utf-8

import datetime
import random
import sys
import uuid
import gibberis.ch.freeform

import os
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    print "Please set DJANGO_SETTINGS_MODULE to your projects settings module"
    sys.exit(1)
print "Using DJANGO_SETTINGS_MODULE=%s" % os.environ['DJANGO_SETTINGS_MODULE']

from ebpub.db.models import NewsItem, Schema
from ebpub.streets.models import Block
lookup_vals = ['lookup_%02d' % i for i in range(30)]

cache = {}
def get_text_corpus():
    if not cache.has_key('corpus'):
        url = 'http://www.gutenberg.org/ebooks/33661.txt.utf8'
        outfile = '/tmp/' + url.split('/')[-1]
        if not os.path.exists(outfile):
            import urllib2
            data = urllib2.urlopen(url).read()
            open(outfile, 'w').write(data)
        cache['corpus'] = open(outfile).read()
    return cache['corpus']

def save_random_newsitem(schema, i, block):
    title = '%d Random %s %s' % (i, schema.name, uuid.uuid4())
    print "Creating %r" % title
    item = NewsItem(title=title, schema=schema)
    item.description = gibberis.ch.freeform.random_text(get_text_corpus(), 300)
    item.url = 'http://example.com/%s/%d' % (schema.slug, i)
    date = random_datetime(7.0)
    item.pub_date = date
    item.item_date = date.date()
    item.location_name = block.pretty_name
    item.block = block
    try:
        item.location = block.geom.centroid
    except AttributeError:
        item.location = block.geom
    # Populate the attributes.
    attrs = {}
    for schemafield in schema.schemafield_set.all():
        attrs[schemafield.name] = random_schemafield_value(schemafield)

    print "Added: %s at %s (%s)" % (item.title, item.location_name, item.location.wkt)
    item.save()
    if attrs:
        item.attributes = attrs
        # That implicitly saves.


def main(count, slugs):
    """
    Generates `count` random newsitems for each schema in `slugs`.
    """
    schemas = Schema.objects.filter(slug__in=slugs)
    if len(schemas) < len(slugs):
        raise ValueError("Bad schema argument. Valid schemas: %s"
                         % ', '.join([s.slug for s in Schema.objects.all()]))
    blocks = get_random_blocks()
    for schema in schemas:
        last_newsitem = NewsItem.objects.order_by('-id')[:1]
        if last_newsitem:
            last_newsitem_id = last_newsitem[0].id
        else:
            last_newsitem_id = 1
        for i in range(int(count)):
            block = random.choice(blocks)
            save_random_newsitem(schema, i + 1 + last_newsitem_id, block)

def get_random_blocks():
    try:
        last_block_id = Block.objects.order_by('-id')[:1][0].id
    except IndexError:
        raise IndexError("It seems you don't have any Blocks loaded.")
    ids = random.sample(xrange(1, last_block_id), 1000)
    blocks = Block.objects.filter(id__in=ids)
    return blocks

def random_datetime(max_age_days):
    dt = datetime.datetime.now() - datetime.timedelta(
        random.uniform(0.0, max_age_days))
    return dt


def random_schemafield_value(schemafield):
    value = None
    if schemafield.is_lookup:
        from ebpub.db.models import Lookup
        value = []
        if schemafield.is_many_to_many_lookup():
            _count = 3
        else:
            _count = 1
        for i in range(_count):
            lookup = Lookup.objects.get_or_create_lookup(
                schemafield, random.choice(lookup_vals))
            value.append(str(lookup.id))
        value = ','.join(value)

    elif schemafield.datatype == 'int':
        value = random.randint(1, 100)
    elif schemafield.datatype == 'bool':
        value = random.choice((True, False))
    elif schemafield.datatype == 'varchar':
        value = gibberis.ch.freeform.random_text(get_text_corpus(), 15)
    elif schemafield.datatype == 'text':
        value = gibberis.ch.freeform.random_text(get_text_corpus(), 100)
    elif schemafield.datatype == 'datetime':
        value = random_datetime(7.0)
    elif schemafield.datatype == 'date':
        value = random_datetime(7.0).date()
    elif schemafield.datatype == 'time':
        value = random_datetime(7.0).time()
    else:
        raise NotImplementedError("can't handle type %s" % schemafield.datatype)
    if value is None:
        raise ValueError("couldn't cook a value for %s.%s" % (
                schemafield.schema, schemafield.name))
    return value


if __name__ == '__main__':
    try:
        count = sys.argv[1]
        schemas = sys.argv[2:]
        if not schemas:
            raise IndexError()
    except IndexError:
        sys.stderr.write("Usage: %s N schema [schema2...]\n" % sys.argv[0])
        sys.stderr.write("Generates N randomly-placed articles for each schema.\n")
        sys.exit(1)
    sys.exit(main(count, schemas))

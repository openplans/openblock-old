#!/usr/bin/env python
# encoding: utf-8
import sys, feedparser, datetime
from optparse import OptionParser

from django.contrib.gis.geos import Point

from ebpub.db.models import NewsItem, Schema

# Note there's an undocumented assumption in ebdata that we want to
# put unescape html before putting it in the db.  Maybe wouldn't have
# to do this if we used the scraper framework in ebdata?
# ... nope, you have to clean up manually.
from ebdata.retrieval.utils import convert_entities

def main(argv=None):
    if argv:
        url = argv[0]
    else:
        url = 'http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&subject=massachusetts&scope=bonzai'
    schema = 'local-news'

    try:
        schema = Schema.objects.get(slug=schema)
    except Schema.DoesNotExist:
        print "Schema (%s): DoesNotExist" % schema
        sys.exit(1)

    f = feedparser.parse(url)

    for e in f.entries:
        try:
            item = NewsItem.objects.get(title=e.title, description=e.description)
            print "Already have %r (id %d)" % (item.title, item.id)
        except NewsItem.DoesNotExist:
            item = NewsItem()
        try:
            item.schema = schema
            item.title = convert_entities(e.title)
            item.description = convert_entities(e.description)
            item.url = e.link
            item.location_name = e.get('x-calconnect-street') or e.get('georss_featurename')
            item.item_date = datetime.datetime(*e.updated_parsed[:6])
            item.pub_date = datetime.datetime(*e.updated_parsed[:6])
            if 'point' in e:
                x,y = e.point.split(' ')
            elif 'georss_point' in e:
                x,y = e.georss_point.split(' ')
            else:
                text = item.title + ' ' + item.description
                from geocoder_hack import quick_dirty_fallback_geocode
                x, y = quick_dirty_fallback_geocode(text, parse=True)
                if None in (x, y):
                    print " couldn't geocode '%s...'" % item.title[:30]
                    continue
            item.location = Point((float(y), float(x)))
            if item.location.x == 0.0 and item.location.y == 0.0:
                # There's a lot of these. Maybe attempt to
                # parse and geocode if we haven't already?
                print "Skipping %r as it has bad location 0,0" % item.title
                continue
            if not item.location_name:
                # Fall back to reverse-geocoding.
                from ebpub.geocoder import reverse
                try:
                    block, distance = reverse.reverse_geocode(item.location)
                    print " Reverse-geocoded point to %r" % block.pretty_name
                    item.location_name = block.pretty_name
                except reverse.ReverseGeocodeError:
                    print " Failed to reverse geocode %s for %r" % (item.location.wkt, item.title)
                    item.location_name = u''
            item.save()
            print "Saved: %s" % item.title
        except:
            print "Warning: couldn't save %r. Traceback:" % item.title
            import cStringIO, traceback
            f = cStringIO.StringIO()
            traceback.print_exc(file=f)
            msg = f.getvalue()
            print msg

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

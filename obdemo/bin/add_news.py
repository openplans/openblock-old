#!/usr/bin/env python
# encoding: utf-8
import sys, feedparser, datetime
from optparse import OptionParser

from django.contrib.gis.geos import Point

from ebpub.db.models import NewsItem, Schema
from ebpub.geocoder import SmartGeocoder

# Note there's an undocumented assumption in ebdata that we want to
# put unescape html before putting it in the db.  Maybe wouldn't have
# to do this if we used the scraper framework in ebdata?
from ebdata.retrieval.utils import convert_entities

def main(argv=None):
    url = 'http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&subject=boston&scope=bonzai'
    schema = 'local-news'
    
    try:
        schema = Schema.objects.get(slug=schema)
    except Schema.DoesNotExist:
        print "Schema (%s): DoesNotExist" % schema
        sys.exit(0)
        
    f = feedparser.parse(url)
    geocoder = SmartGeocoder()
    
    for e in f.entries:
        try:
            item = NewsItem.objects.get(title=e.title, description=e.description)
            print "Already have %r (id %d)" % (item.title, item.id)
        except NewsItem.DoesNotExist:
            item = NewsItem()
            item.schema = schema
            item.title = convert_entities(e.title)
            item.description = convert_entities(e.description)
            item.url = e.link
            #item.location_name = e['x-calconnect-street']
            item.item_date = datetime.datetime(*e.updated_parsed[:6])
            item.pub_date = datetime.datetime(*e.updated_parsed[:6])
        
            try:
                if 'point' in e:
                    x,y = e.point.split(' ')
                else:
                    x,y = e.georss_point.split(' ')
                item.location = Point((float(y), float(x)))
                if item.location.x == 0.0 and item.location.y == 0.0:
                    # There's a lot of these. Maybe attempt to
                    # re-parse the article using ebdata.nlp.addresses
                    # and re-geocode using ebpub.geocoder?
                    print "Skipping %r as it has bad location 0,0" % item.title
                else:
                    item.save()
                    print "Added: %s" % item.title
            except:
                print "Warning: couldn't save. Traceback:"
                import cStringIO, traceback
                f = cStringIO.StringIO()
                traceback.print_exc(file=f)
                msg = f.getvalue()
                print msg
        
    
if __name__ == '__main__':
    sys.exit(main())

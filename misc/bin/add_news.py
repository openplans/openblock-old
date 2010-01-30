#!/usr/bin/env python
# encoding: utf-8
import sys, feedparser, datetime
from optparse import OptionParser

from django.contrib.gis.geos import Point

from ebpub.db.models import NewsItem, Schema
from ebpub.geocoder import SmartGeocoder

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
        except NewsItem.DoesNotExist:
            item = NewsItem()
            item.schema = schema
            item.title = e.title
            item.description = e.description
            item.url = e.link
            #item.location_name = e['x-calconnect-street']
            item.item_date = datetime.datetime(*e.updated_parsed[:6])
            item.pub_date = datetime.datetime(*e.updated_parsed[:6])
        
            try:
                x,y = e.point.split(' ')
                item.location = Point((float(y), float(x)))
                item.save()
            except:
                pass
        
            print "Added: %s" % item.title
    
if __name__ == '__main__':
    sys.exit(main())

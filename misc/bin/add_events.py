#!/usr/bin/env python
# encoding: utf-8
import sys, feedparser, datetime
from optparse import OptionParser

from django.contrib.gis.geos import Point

from ebpub.db.models import NewsItem, Schema
from ebpub.geocoder import SmartGeocoder

def main(argv=None):
    url = 'http://calendar.boston.com/search?acat=&cat=&commit=Search&new=n&rss=1&search=true&sort=0&srad=20&srss=50&ssrss=5&st=event&st_select=any&svt=text&swhat=&swhen=today&swhere=&trim=1'
    schema = 'events'
    
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
            item.location_name = e['x-calconnect-street']
            item.item_date = datetime.datetime.strptime(e.dtstart, 
                "%Y-%m-%d %H:%M:%S +0000")
            item.pub_date = datetime.datetime(*e.updated_parsed[:6])
        
            try:
                add = geocoder.geocode(item.location_name)
                item.location = add['point']
                item.block = add['block']
            except:
                pass
                
            item.save()
        
            print "Added: %s" % item.title
    
if __name__ == '__main__':
    sys.exit(main())


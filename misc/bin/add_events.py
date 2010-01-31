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
    
    parser = OptionParser()
    parser.add_option('-q', '--quiet', action="store_true", dest="quiet", 
        default=False, help="no output")
        
    (options, args) = parser.parse_args()
    
    try:
        schema = Schema.objects.get(slug=schema)
    except Schema.DoesNotExist:
        print "Schema (%s): DoesNotExist" % schema
        sys.exit(0)
        
    f = feedparser.parse(url)
    geocoder = SmartGeocoder()
    
    for e in f.entries:
        try:
            item = NewsItem.objects.get(title=e.title, 
                description=e.description)
            status = "Updated"
        except NewsItem.DoesNotExist:
            item = NewsItem()
            status = "Added"
        
        try:
            item.schema = schema
            item.title = e.title
            item.description = e.description
            item.url = e.link
            item.item_date = datetime.datetime(*e.updated_parsed[:6])
            item.pub_date = datetime.datetime(*e.updated_parsed[:6])
            item.location = Point((float(e['geo_long']), 
                float(e['geo_lat'])))
            item.save()
            if not options.quiet:
                print "%s: %s" % (status, item.title)
        except e:
            pass
        
    
if __name__ == '__main__':
    sys.exit(main())


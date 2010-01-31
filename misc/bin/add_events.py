#!/usr/bin/env python
# encoding: utf-8
#pylint: disable-msg=E1101
#pylint: disable-msg=W0142

"""
add_events.py

Created by Don Kukral <don_at_kukral_dot_org>

Downloads calendar entries from RSS feed at boston.com 
and updates the database
"""

import sys, feedparser, datetime
from optparse import OptionParser

from django.contrib.gis.geos import Point

from ebpub.db.models import NewsItem, Schema

def main():
    """ Download Calendar RSS feed and update database """

    url = """http://calendar.boston.com/search?acat=&cat=&commit=Search\
&new=n&rss=1&search=true&sort=0&srad=20&srss=50&ssrss=5&st=event\
&st_select=any&svt=text&swhat=&swhen=today&swhere=&trim=1"""
    schema = 'events'
    
    parser = OptionParser()
    parser.add_option('-q', '--quiet', action="store_true", dest="quiet", 
        default=False, help="no output")
        
    (options, args) = parser.parse_args()

    if len(args) > 0:
        return parser.error('script does not take any arguments')
    
    try:
        schema = Schema.objects.get(slug=schema)
    except Schema.DoesNotExist:
        print "Schema (%s): DoesNotExist" % schema
        sys.exit(0)
        
    feed = feedparser.parse(url)
    
    for entry in feed.entries:
        try:
            item = NewsItem.objects.get(title=entry.title, 
                description=entry.description)
            status = "Updated"
        except NewsItem.DoesNotExist:
            item = NewsItem()
            status = "Added"
        
        try:
            item.schema = schema
            item.title = entry.title
            item.description = entry.description
            item.url = entry.link
            item.item_date = datetime.datetime(*entry.updated_parsed[:6])
            item.pub_date = datetime.datetime(*entry.updated_parsed[:6])
            item.location = Point((float(entry['geo_long']), 
                float(entry['geo_lat'])))
            item.save()
            if not options.quiet:
                print "%s: %s" % (status, item.title)
        except ValueError:
            if not options.quiet:
                print "unexpected error:", sys.exc_info()[1]
            
if __name__ == '__main__':
    sys.exit(main())


#!/usr/bin/env python
# encoding: utf-8
#pylint: disable-msg=E1101
#pylint: disable-msg=W0142

"""
add_news.py

Created by Don Kukral <don_at_kukral_dot_org>

Downloads news from RSS feed at boston.com and updates the database
"""

import sys, feedparser, datetime
from optparse import OptionParser

from django.contrib.gis.geos import Point

from ebpub.db.models import NewsItem, Schema

def main():
    """ Download News RSS feed and update database """
    
    url = """http://search.boston.com/search/api?q=*\
&sort=-articleprintpublicationdate&subject=boston&scope=bonzai"""
    schema = 'local-news'

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

        item.schema = schema
        item.title = entry.title
        item.description = entry.description
        item.url = entry.link
        item.item_date = datetime.datetime(*entry.updated_parsed[:6])
        item.pub_date = datetime.datetime(*entry.updated_parsed[:6])
        
        try:
            if 'point' in entry:
                lat, lng = entry.point.split(' ')
            else:
                lat, lng = entry.georss_point.split(' ')
            item.location = Point((float(lng), float(lat)))
            item.save()
        except (ValueError, AttributeError):
            if not options.quiet:
                print "unexpected error:", sys.exc_info()[1]
        
        if not options.quiet:
            print "%s: %s" % (status, item.title)
    
if __name__ == '__main__':
    sys.exit(main())
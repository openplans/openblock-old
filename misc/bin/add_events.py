#!/usr/bin/env python
# encoding: utf-8
import sys, feedparser, datetime
from optparse import OptionParser

from django.contrib.gis.geos import Point

from ebpub.db.models import NewsItem, Schema


def main(argv=None):
    parser = OptionParser(usage="""
%prog schema rss_url
    
Arguments:
  schema               e.g., "events" # slug of schema
  rss_url              e.g., "http://somedomain.com/events/rss" # url of feed
""")

#    parser.add_option("-b", "--browsable", #action="store_false", 
#        dest="browsable", default=True, 
#        help="whether this is displayed on location_type_list")
        
    (options, args) = parser.parse_args()
    if len(args) != 2: 
        return parser.error('must provide 2 arguments, see usage')
    
    try:
        schema = Schema.objects.get(slug=args[0])
    except Schema.DoesNotExist:
        print "Schema (%s): DoesNotExist" % args[0]
        sys.exit(0)
        
    f = feedparser.parse(args[1])
    
    for e in f.entries:
        item = NewsItem()
        item.schema = schema
        item.title = e.title
        item.description = e.description
        item.url = e.link
        item.location_name = e['x-calconnect-street']
#        lat = float(e.geo_lat)
#        lng = float(e.geo_long)
#        item.location = Point((lat, lng))
        item.item_date = datetime.datetime.strptime(e.dtstart, 
            "%Y-%m-%d %H:%M:%S +0000")
        item.pub_date = datetime.datetime(*e.updated_parsed[:6])
        
        item.save()
        
        print "Added: %s" % item.title
        
        
if __name__ == '__main__':
    sys.exit(main())


#    schema = models.ForeignKey(Schema)
#    title = models.CharField(max_length=255)
#    description = models.TextField()
#    url = models.TextField(blank=True)
#    pub_date = models.DateTimeField(db_index=True)
#    item_date = models.DateField(db_index=True)
#    location = models.GeometryField(blank=True, null=True)
#    location_name = models.CharField(max_length=255)
#    location_object = models.ForeignKey(Location, blank=True, null=True)
#    block = models.ForeignKey(Block, blank=True, null=True)
#    objects = NewsItemManager()
#    attributes = AttributesDescriptor()

#!/usr/bin/env python
# encoding: utf-8
import sys
from optparse import OptionParser

from django.contrib.gis.geos import Polygon

from ebpub.db.models import Location
from ebpub.db.models import LocationType


def main(argv=None):
    parser = OptionParser(usage="""
%prog name normalized_name slug location_type city source sw ne
    
Arguments: 
  name                 e.g., "35th Ward"
  normalized_name      e.g., "35th Ward"
  slug                 e.g., "35th-ward"
  location_type        e.g., "neighborhoods" (slug of locationtype)
  city                 e.g., "Chicago"
  source               e.g., "Source of Location"
  sw                   e.g., "42.355282, -71.073530" (SW Corner)
  ne                   e.g., "42.361259, -71.059794" (NE Corner)
""")

    (options, args) = parser.parse_args()
    if len(args) != 8: 
        return parser.error('must provide all 8 arguments, see usage')
    
    try:
        loctype = LocationType.objects.get(slug=args[3])
    except LocationType.DoesNotExist:
        print "LocationType (%s): DoesNotExist" % args[3]
        sys.exit(0)
        
    l = Location()
    l.name = args[0]
    l.normalized_name = args[1]
    l.slug = args[2]
    l.location_type = loctype
    l.city = args[4]
    l.source = args[5]
    
    try:
        sw = args[6].split(",")
        ne = args[7].split(",")
        box = (float(sw[0]), float(sw[1]), float(ne[0]), float(ne[1]))
        poly = Polygon.from_bbox(box)
    except ValueError:
        return parser.error('error parsing sw and ne coordinates')
    
    l.location = poly
    l.is_public = True
    l.display_order = 1
    l.save()

if __name__ == '__main__':
    sys.exit(main())

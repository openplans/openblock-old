#!/usr/bin/env python
# encoding: utf-8
#pylint: disable-msg=E1101
#pylint: disable-msg=W0142
#pylint: disable-msg=W0612

"""
add_location.py

Created by Don Kukral <don_at_kukral_dot_org>

Adds a location to the database
"""

import sys
from optparse import OptionParser
from django.contrib.gis.geos import Polygon
from ebpub.db.models import Location
from ebpub.db.models import LocationType

def main():
    """ add a location to the database """
    
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
        
    location = Location()
    location.name = args[0]
    location.normalized_name = args[1]
    location.slug = args[2]
    location.location_type = loctype
    location.city = args[4]
    location.source = args[5]
    
    try:
        southwest = args[6].split(",")
        northeast = args[7].split(",")
        box = (float(southwest[1]), float(southwest[0]), 
            float(northeast[1]), float(northeast[0]))
        poly = Polygon.from_bbox(box)
    except ValueError:
        return parser.error('error parsing sw and ne coordinates')
    
    location.location = poly
    location.is_public = True
    location.display_order = 1
    location.save()

if __name__ == '__main__':
    sys.exit(main())

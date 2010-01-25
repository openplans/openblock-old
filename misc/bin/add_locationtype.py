#!/usr/bin/env python
# encoding: utf-8
import sys
from optparse import OptionParser

from ebpub.db.models import LocationType


def main(argv=None):
    parser = OptionParser(usage="""
%prog name plural_name scope slug
    
Arguments: 
  name                 e.g., "Ward" or "Congressional District"
  plural_name          e.g., "Wards"
  scope                e.g., "Chicago" or "U.S.A."
  slug                 e.g., "chicago", "usa" """)

    parser.add_option("-b", "--browsable", #action="store_false", 
        dest="browsable", default=True, 
        help="whether this is displayed on location_type_list")
    parser.add_option("-s", "--significant", #action="store_false", 
        dest="significant", default=True, 
        help="whether this is used to display aggregates, etc.")
        
    (options, args) = parser.parse_args()
    if len(args) != 4: 
        return parser.error('must provide 4 arguments, see usage')
    
    location_type = LocationType()
    location_type.name = args[0]
    location_type.plural_name = args[1]
    location_type.scope = args[2]
    location_type.slug = args[3]
    location_type.is_browsable = options.browsable
    location_type.is_significant = options.significant
    location_type.save()
    
if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python
# encoding: utf-8
import datetime, sys
from optparse import OptionParser

from ebpub.db.models import Schema, SchemaInfo


def main(argv=None):
    parser = OptionParser(usage="""
%prog name plural_name slug description summary source
    
Arguments: 
  name                 e.g., "Crime" or "Event"
  plural_name          e.g., "Crimes"
  slug                 e.g., "crimes", "events" 
  description          e.g., "List of crimes provided by the local Police Dept"
  summary              e.g., "List of crimes"
  source               e.g., "http://google.com/query=crimes"
  """)

    (options, args) = parser.parse_args()
    if len(args) != 6: 
        return parser.error('must provide 6 arguments, see usage')
    
    schema = Schema()
    schema.name = args[0]
    schema.plural_name = args[1]
    schema.slug = args[2]
    
    #  need to allow this as an input later
    schema.indefinite_article = 'a' 
    schema.min_date = datetime.date(2009,1,1)
    schema.last_updated = datetime.date(2009,1,1) 
    schema.date_name = "Date"
    schema.date_name_plural = "Dates"
    schema.importance = 100
    schema.is_public = True
    schema.is_special_report = False
    schema.can_collapse = True
    schema.has_newsitem_detail = True
    schema.allow_charting = True
    schema.uses_attributes_in_list = True
    schema.number_in_overview = 5
    
    schema.save()
    
    schemainfo = SchemaInfo()
    schemainfo.schema = schema
    schemainfo.short_description = args[3]
    schemainfo.summary = args[4]
    schemainfo.source = args[5]
    schemainfo.short_source = schemainfo.source[:128]
    schemainfo.update_frequency = ''
    schemainfo.intro = ''
    
    schemainfo.save()


if __name__ == '__main__':
    sys.exit(main())



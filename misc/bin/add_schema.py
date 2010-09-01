#!/usr/bin/env python
# encoding: utf-8
#pylint: disable-msg=W0612
"""
add_schema.py

Created by Don Kukral <don_at_kukral_dot_org>

Adds a schema to the database
"""

import datetime, sys
from optparse import OptionParser

from ebpub.db.models import Schema, SchemaInfo, SchemaField


def main():
    """ add a schema to the database """
    parser = OptionParser(usage="""
%prog name plural_name slug description summary source
    
Arguments: 
  name                 e.g., "Crime" or "Event"
  plural_name          e.g., "Crimes"
  slug                 e.g., "crimes", "events" 
  description          e.g., "List of crimes provided by the local Police Dept"
  summary              e.g., "List of crimes"
  source               e.g., "http://google.com/query=crimes"
  [fieldname real_name pretty_name pretty_name_plural display is_lookup is_filter is_searchable ...]    optional SchemaFields, see ebpub/README.txt
  """)

    parser.add_option("-f", "--force", dest="force", action="store_true",
                      help="force deletion of existing schema")

    (options, args) = parser.parse_args()
    if len(args) < 6: 
        return parser.error('must provide 6 arguments, see usage')
    
    slug = args[2]
    if options.force:
        Schema.objects.filter(slug=slug).delete()

    schema = Schema()
    schema.name = args[0]
    schema.plural_name = args[1]
    schema.slug = slug
    
    #  need to allow this as an input later
    schema.indefinite_article = 'a' 
    schema.min_date = datetime.date(2009, 1, 1)
    schema.last_updated = datetime.date(2009, 1, 1) 
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

    if len(args) > 6:
        # TODO: allow more than one SchemaField.
        # TODO: this is a horrible UI, move to separate script?
        field = SchemaField()
        field.schema = schema
        field.name = args[6]
        field.real_name = args[7] # The column to use in the
        # db_attribute model. Choices are: int01-07, text01,
        # bool01-05, datetime01-04, date01-05, time01-02,
        # varchar01-05. This value must be unique with respect to the
        # schema_id.
        field.pretty_name = args[8]
        field.pretty_name_plural = args[9]
        field.display = bool(int(args[10]))
        field.is_lookup = bool(int(args[11]))
        field.is_filter = bool(int(args[12]))
        field.is_charted = bool(int(args[13]))
        field.display_order = bool(int(args[14]))
        field.is_searchable = bool(int(args[15]))
        field.save()

if __name__ == '__main__':
    sys.exit(main())



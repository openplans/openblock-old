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

from ebpub.db.models import Schema


def main():
    """ add a schema to the database """
    parser = OptionParser()
    parser.add_option("-f", "--force", action="store_true",
                      help="force deletion of existing schema")

    parser.add_option('-n', '--name')
    parser.add_option('--plural-name', default='')
    parser.add_option('-s', '--slug', default='')
    parser.add_option('--description', dest="short_description")
    parser.add_option('--summary')
    parser.add_option('--source')
    (options, args) = parser.parse_args()
    return add_schema(**options.__dict__)


def add_schema(name, short_description, summary, source,
               slug=None, plural_name=None,
               force=False):
    # Derive plural_name and slug from name, if necessary.
    if not plural_name:
        if name.endswith('s'):
            plural_name = name
        else:
            plural_name = name + 's'
    slug = slug or '-'.join(plural_name.split()).lower()

    if force:
        Schema.objects.filter(slug=slug).delete()

    schema = Schema()
    schema.name = name
    schema.plural_name = plural_name
    schema.slug = slug
    
    #  TODO: need to allow these as inputs later.
    if name[0].lower() in 'aeiou':
        schema.indefinite_article = 'an' 
    else:
        schema.indefinite_article = 'a'
    schema.min_date = datetime.date(2009, 1, 1)
    schema.last_updated = datetime.date.today()
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
    schema.short_description = short_description
    schema.summary = summary
    schema.source = source

    # TODO: make these parameters
    schema.short_source = schema.source[:128]
    schema.update_frequency = ''
    schema.intro = ''

    schema.save()


if __name__ == '__main__':
    sys.exit(main())

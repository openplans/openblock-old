#!/usr/bin/env python
# encoding: utf-8

#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#

#pylint: disable-msg=W0612
"""
add_schemafield.py

Adds a schemafield to the database.
"""

import sys
from optparse import OptionParser
from ebpub.db.models import Schema, SchemaField


def main():
    """ add a schema to the database """
    parser = OptionParser()
    parser.add_option("-f", "--force", action="store_true",
                      help="force deletion of existing schemafield")
    parser.add_option('-s', '--schema-slug', dest="slug")
    parser.add_option('-n', '--name')
    parser.add_option('-r', '--real-name')
    parser.add_option('--pretty-name')
    parser.add_option('--pretty-name-plural', default='')
    parser.add_option('--display', default=False, action="store_true")
    parser.add_option('--display-order', default=0, type="int")
    parser.add_option('--is-lookup', default=False, action="store_true")
    parser.add_option('--is-filter', default=False, action="store_true")
    parser.add_option('--is-searchable', default=False, action="store_true")
    parser.add_option('--is-charted', default=False, action="store_true")
    (options, args) = parser.parse_args()
    return add_schemafield(**options.__dict__)
    
def add_schemafield(slug, name, real_name,
                    pretty_name, pretty_name_plural=None,
                    display=True, display_order=0, 
                    is_lookup=False, is_filter=False,
                    is_searchable=True, is_charted=False,
                    force=False):

    # Deliberately blows up if no such schema.
    schema = Schema.objects.filter(slug=slug)[0]

    if force:
        SchemaField.objects.filter(schema=schema, real_name=real_name).delete()

    field = SchemaField()
    field.schema = schema
    # db_attribute model. Choices are: int01-07, text01,
    # bool01-05, datetime01-04, date01-05, time01-02,
    # varchar01-05. This value must be unique with respect to the
    # schema_id.
    field.real_name = real_name

    field.name = name
    field.pretty_name = pretty_name
    if not pretty_name_plural:
        if pretty_name.endswith('s'):
            pretty_name_plural = pretty_name
        else:
            pretty_name_plural = pretty_name + 's'
    field.pretty_name_plural = pretty_name_plural
    field.display = display
    field.is_lookup = is_lookup
    field.is_filter = is_filter
    field.is_charted = is_charted
    field.display_order = display_order
    field.is_searchable = is_searchable
    field.save()

if __name__ == '__main__':
    sys.exit(main())

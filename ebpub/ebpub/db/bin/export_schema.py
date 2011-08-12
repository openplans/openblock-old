#!/usr/bin/env python
#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

from ebpub.db.models import Schema

fixbool = lambda x: bool(x) and 't' or 'f'

def get_value(obj, field):
    if field.get_internal_type() == 'BooleanField':
        return fixbool(getattr(obj, field.attname))
    else:
        return getattr(obj, field.attname)

def escape(value):
    if isinstance(value, (int, long)):
        return str(value)
    else:
        return "'%s'" % str(value).replace("'", "''")

def get_cols_vals_for_insert(model):
    # Don't copy the primary key id field or related fields
    fields = [f for f in model._meta.fields if f.get_internal_type() not in ('AutoField', 'ForeignKey')]
    cols = [f.column for f in fields]
    values = [escape(get_value(model, f)) for f in fields]
    return (cols, values)

def get_insert_sql(table, cols, values):
    cols_clause = '(' + ', '.join(cols) + ')'
    values_clause = '(' + ', '.join(values) + ')'
    return 'INSERT INTO %s %s VALUES %s;' % (table, cols_clause, values_clause)
    
def print_schema_creation(schema_slug):
    s = Schema.objects.get(slug=schema_slug)
    print "BEGIN;"
    print get_insert_sql(s._meta.db_table, *get_cols_vals_for_insert(s))
    for sf in s.schemafield_set.all():
        cols, vals = get_cols_vals_for_insert(sf)
        cols.insert(0, 'schema_id')
        vals.insert(0, "(SELECT id FROM %s WHERE slug='%s')" % (s._meta.db_table, s.slug))
        print get_insert_sql(sf._meta.db_table, cols, vals)
    print "COMMIT;"

def main():
    import sys
    print_schema_creation(sys.argv[1])

if __name__ == "__main__":
    main()

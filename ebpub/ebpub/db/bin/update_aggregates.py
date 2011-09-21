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

from django.conf import settings
from django.db import connection, transaction
from ebpub.db import constants
from ebpub.db.models import Schema, SchemaField, NewsItem, AggregateAll, AggregateDay, AggregateLocationDay, AggregateLocation, AggregateFieldLookup
from ebpub.db.utils import today
from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
import datetime
import logging

logger = logging.getLogger('ebpub.db.bin.update_aggregates')

def smart_update(cursor, new_values, table_name, field_names, comparable_fields,
                 where, pk_name='id', dry_run=False):
    # new_values is a list of dictionaries, each with a value for each field in field_names.

    # Run a query to determine the current values in the DB.
    where = where.items()
    cursor.execute("""
        SELECT %s, %s
        FROM %s
        WHERE %s""" % (pk_name, ','.join(field_names), table_name,
            ' AND '.join(['%s=%%s' % k for k, v in where])), tuple([v for k, v in where]))
    old_values = dict([(tuple(row[1:len(comparable_fields)+1]), dict(zip((pk_name,)+field_names, row))) for row in cursor.fetchall()])
    for new_value in new_values:
        key = tuple([new_value[i] for i in comparable_fields])
        try:
            old_value = old_values.pop(key)
        except KeyError:
            logger.debug(
                "INSERT INTO %s (%s) VALUES (%s)" % (table_name, ', '.join(field_names + tuple([i[0] for i in where])), ', '.join([str(new_value[i]) for i in field_names] + [str(i[1]) for i in where])))
            if not dry_run:
                cursor.execute("INSERT INTO %s (%s) VALUES (%s)" % \
                    (table_name, ', '.join(field_names + tuple([i[0] for i in where])), ','.join(['%s' for _ in tuple(field_names) + tuple(where)])),
                    tuple([new_value[i] for i in field_names] + [i[1] for i in where]))
        else:
            for k, v in new_value.items():
                if old_value[k] != v:
                    logger.debug(
                        "UPDATE %s SET %s WHERE %s=%s" % (table_name, ', '.join(['%s=%s' % (k, v) for k, v in new_value.items()]), pk_name, old_value[pk_name]))
                    if not dry_run:
                        new_value_tuple = new_value.items()
                        cursor.execute("UPDATE %s SET %s WHERE %s=%%s" % \
                            (table_name, ', '.join(['%s=%%s' % k for k, v in new_value_tuple]), pk_name),
                            tuple([v for k, v in new_value_tuple] + [old_value[pk_name]]))
                    break
    for old_value in old_values.values():
        logger.debug("DELETE FROM %s WHERE %s = %s" % (table_name, pk_name, old_value[pk_name]))
        if not dry_run:
            cursor.execute("DELETE FROM %s WHERE %s = %%s" % (table_name, pk_name), (old_value[pk_name],))

def update_aggregates(schema_id_or_slug, dry_run=False,  reset=False):
    """
    Updates all Aggregate* tables for the given schema_id/slug,
    deleting/updating the existing records if necessary.

    If dry_run is True, then the records won't be updated -- only the SQL
    will be output.

    If reset is True, then all aggregates for this schema will be deleted before
    updating.
    """
    logger.info('... %s' % schema_id_or_slug)
    if not str(schema_id_or_slug).isdigit():
        schema_id = Schema.objects.get(slug=schema_id_or_slug).id
    else:
        schema_id = schema_id_or_slug
    cursor = connection.cursor()

    if reset and not dry_run:
        for aggmodel in (AggregateAll, AggregateDay, AggregateLocation,
                         AggregateLocationDay, AggregateFieldLookup):
            logger.info('... deleting all %s for schema %s' % (aggmodel.__name__, schema_id_or_slug))
            aggmodel.objects.filter(schema__id=schema_id).delete()

    # AggregateAll
    cursor.execute("SELECT COUNT(*) FROM db_newsitem WHERE schema_id = %s", (schema_id,))
    new_values = [{'total': row[0]} for row in cursor.fetchall()]
    smart_update(cursor, new_values, AggregateAll._meta.db_table, ('total',),
                 (), {'schema_id': schema_id}, dry_run=dry_run)

    # AggregateDay
    cursor.execute("""
        SELECT item_date, COUNT(*)
        FROM db_newsitem
        WHERE schema_id = %s
        GROUP BY 1""", (schema_id,))
    new_values = [{'date_part': row[0], 'total': row[1]} for row in cursor.fetchall()]
    smart_update(cursor, new_values, AggregateDay._meta.db_table, ('date_part', 'total'),
                 ('date_part',), {'schema_id': schema_id}, dry_run=dry_run,
                 )

    # AggregateLocationDay
    cursor.execute("""
        SELECT nl.location_id, ni.item_date, loc.location_type_id, COUNT(*)
        FROM db_newsitemlocation nl, db_newsitem ni, db_location loc
        WHERE nl.news_item_id = ni.id
            AND ni.schema_id = %s
            AND nl.location_id = loc.id
        GROUP BY 1, 2, 3""", (schema_id,))
    new_values = [{'location_id': row[0], 'date_part': row[1], 'location_type_id': row[2], 'total': row[3]} for row in cursor.fetchall()]
    smart_update(cursor, new_values, AggregateLocationDay._meta.db_table, ('location_id', 'date_part', 'location_type_id', 'total'),
                 ('location_id', 'date_part', 'location_type_id'),
                 {'schema_id': schema_id}, dry_run=dry_run,
                 )

    # AggregateLocation
    # This query is a bit clever -- we just sum up the totals created in a
    # previous aggregate. It's a helpful optimization, because otherwise
    # the location query is way too slow.
    # Note that we calculate the total for the last 30 days that had at least
    # one news item -- *NOT* the last 30 days, period.
    # We add date_part <= current_date here to keep sparse items in the future
    # from throwing off counts for the previous 30 days.
    cursor.execute("SELECT date_part FROM %s WHERE schema_id = %%s AND date_part <= current_date ORDER BY date_part DESC LIMIT 1" % \
        AggregateLocationDay._meta.db_table, (schema_id,))
    try:
        end_date = cursor.fetchone()[0]
    except TypeError: # if cursor.fetchone() is None, there are no records.
        pass
    else:
        # Note that BETWEEN is inclusive on both ends, so to get
        # AggregateLocationDays for eg. 30 days, we'd need a timedelta of 29
        start_date = end_date - constants.DAYS_AGGREGATE_TIMEDELTA
        cursor.execute("""
            SELECT location_id, location_type_id, SUM(total)
            FROM %s
            WHERE schema_id = %%s
                AND date_part BETWEEN %%s AND %%s
            GROUP BY 1, 2""" % AggregateLocationDay._meta.db_table,
                (schema_id, start_date, end_date))
        new_values = [{'location_id': row[0], 'location_type_id': row[1], 'total': row[2]} for row in cursor.fetchall()]
        smart_update(cursor, new_values, AggregateLocation._meta.db_table,
                     ('location_id', 'location_type_id', 'total'),
                     ('location_id', 'location_type_id'), {'schema_id': schema_id},
                     dry_run=dry_run,
                     )

    for sf in SchemaField.objects.filter(schema__id=schema_id, is_filter=True, is_lookup=True):
        try:
            end_date = NewsItem.objects.filter(schema__id=schema_id, item_date__lte=today()).values_list('item_date', flat=True).order_by('-item_date')[0]
        except IndexError:
            continue # There have been no NewsItems in the given date range.
        # Note BETWEEN is inclusive on both ends.
        start_date = end_date - constants.DAYS_AGGREGATE_TIMEDELTA

        if sf.is_many_to_many_lookup():
            # AggregateFieldLookup
            cursor.execute("""
                SELECT id, (
                    SELECT COUNT(*) FROM db_attribute a, db_newsitem ni
                    WHERE a.news_item_id = ni.id
                        AND a.schema_id = %%s
                        AND ni.schema_id = %%s
                        AND a.%s ~ ('[[:<:]]' || db_lookup.id || '[[:>:]]')
                        AND ni.item_date BETWEEN %%s AND %%s
                )
                FROM db_lookup
                WHERE schema_field_id = %%s""" % sf.real_name, (schema_id, schema_id, start_date, end_date, sf.id))
            new_values = [{'lookup_id': row[0], 'total': row[1]} for row in cursor.fetchall()]
            smart_update(cursor, new_values, AggregateFieldLookup._meta.db_table,
                         ('lookup_id', 'total'), ('lookup_id',),
                         {'schema_id': schema_id, 'schema_field_id': sf.id},
                         dry_run=dry_run,
                         )
        else:
            # AggregateFieldLookup
            cursor.execute("""
                SELECT a.%s, COUNT(*)
                FROM db_attribute a, db_newsitem ni
                WHERE a.news_item_id = ni.id
                    AND a.schema_id = %%s
                    AND ni.schema_id = %%s
                    AND %s IS NOT NULL
                    AND ni.item_date BETWEEN %%s AND %%s
                GROUP BY 1""" % (sf.real_name, sf.real_name), (schema_id, schema_id, start_date, end_date))
            new_values = [{'lookup_id': row[0], 'total': row[1]} for row in cursor.fetchall()]
            smart_update(cursor, new_values, AggregateFieldLookup._meta.db_table,
                         ('lookup_id', 'total'), ('lookup_id',),
                         {'schema_id': schema_id, 'schema_field_id': sf.id},
                         dry_run=dry_run)

    transaction.commit_unless_managed()

def update_all_aggregates(dry_run=False, reset=False):
    for schema in Schema.objects.all():
        if dry_run:
            logger.info('Dry run: Updating %s aggregates' % schema.plural_name)
        elif reset:
            logger.info('Resetting all %s aggregates' % schema.plural_name)
        else:
            logger.info('Updating %s aggregates' % schema.plural_name)
        update_aggregates(schema.id, dry_run=dry_run, reset=reset)

def main(argv=None):
    import sys
    if argv is None:
        argv = sys.argv[1:]
    from optparse import OptionParser
    optparser = OptionParser(usage='''usage: %prog [options] [schema]

Updates aggregate statistics for the given schema (default: all schemas).
''')
    optparser.add_option('-r', '--reset', action='store_true',
                         help='Delete all aggregates before updating.')

    add_verbosity_options(optparser)

    optparser.add_option('-d', '--dry-run', action='store_true',
                         help='Dry run, change nothing.')

    opts, args = optparser.parse_args(argv)


    setup_logging_from_opts(opts, logger)

    if args:
        return update_aggregates(*args, reset=opts.reset, dry_run=opts.dry_run)
    else:
        return update_all_aggregates(reset=opts.reset, dry_run=opts.dry_run)

if __name__ == "__main__":
    main()

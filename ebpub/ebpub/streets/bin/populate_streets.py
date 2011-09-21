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

"""
Populates the street, block intersection, and intersection
model tables.

How to populate intersections
=============================

First import the blocks.

Ensure the ZIP Codes are populated in the db_location table: they
are needed for resolving 'disputes' when the two intersecting
blocks of an intersection have different ZIP Codes. This is
not described here: there should be a ZIP Code importer script
suitable for your city.

Next, populate the streets from the blocks table, by calling populate_streets().

This is the part that takes the longest: populate the
db_blockintersection table. This goes through each block (and
remember, there are on the order of tens of thousands of blocks in
each city) and calculates all the other blocks which intersect with
it. This is inherently slow, even with the heavy-lifting offloaded
to pgsql/postgis. (If we were particularly clever, we'd probably
write our own custom ultra-optimized C module to burn through this
operation. But we're clever enough to recognize that this is a
one-time cost so it's better not to be too cleverer.)

In this module, execute the populate_block_intersections() function.

When that completes, execute the populate_intersections()
function. This is a comparatively fast operation which just looks
up the pre-calculated intersections for each block and creates
a new object representing a particular intersection, eliminating
potential duplicates.
"""

import logging
import sys
import optparse
from django.contrib.gis.geos import fromstr
from django.db import connection, transaction
from ebpub.db.models import Location
from ebpub.metros.allmetros import get_metro
from ebpub.streets.models import Block, BlockIntersection, Intersection, Street
from ebpub.streets.name_utils import make_dir_street_name, pretty_name_from_blocks, slug_from_blocks

logger = logging.getLogger()

def timer(func):
    # a decorator that logs how long func took to run
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        logger.info("Ran %s in %s seconds" % (func.__name__, time.time() - start))
        return result
    return wrapper

def intersecting_blocks(block):
    """
    Returns a list of blocks that intersect the given one.

    Note that blocks with the same street name and suffix are
    excluded -- this is a heuristic that keeps the adjacent blocks
    of the same street out.
    """
    select_list = ["b.%s" % f.name for f in block._meta.fields] + ["ST_Intersection(a.geom, b.geom)"]
    table = block._meta.db_table
    cursor = connection.cursor()
    sql = """
        SELECT %s
        FROM %s a,
             %s b
        WHERE
            a.id = %%s AND
            ST_Intersects(a.geom, b.geom) AND
            GeometryType(ST_Intersection(a.geom, b.geom)) = 'POINT' AND
            NOT (b.street = a.street AND b.suffix = a.suffix)
        ORDER BY
            b.predir, b.street, b.suffix, b.left_from_num, b.right_from_num
        """ % (", ".join(select_list), table, table)
    cursor.execute(sql, [block.id])
    intersections = []
    for row in cursor.fetchall():
        block = Block(*row[:-1])
        intersection_pt = fromstr(row[-1])
        intersections.append((block, intersection_pt))
    return intersections

def intersection_from_blocks(block_a, block_b, intersection_pt, city, state, zip):
    obj = Intersection(
        pretty_name=pretty_name_from_blocks(block_a, block_b),
        slug=slug_from_blocks(block_a, block_b),
        predir_a=block_a.predir,
        street_a=block_a.street,
        suffix_a=block_a.suffix,
        postdir_a=block_a.postdir,
        predir_b=block_b.predir,
        street_b=block_b.street,
        suffix_b=block_b.suffix,
        postdir_b=block_b.postdir,
        city=city,
        state=state,
        zip=zip,
        location=intersection_pt
    )
    return obj

@timer
@transaction.commit_on_success
def populate_streets(*args, **kwargs):
    """
    Populates the streets table from the blocks table
    """
    print 'Populating the streets table'
    Street.objects.all().delete()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO streets (street, pretty_name, street_slug, suffix, city, state)
        SELECT DISTINCT street, street_pretty_name, street_slug, suffix, left_city, left_state
        FROM blocks
        UNION SELECT DISTINCT street, street_pretty_name, street_slug, suffix, right_city, right_state
        FROM blocks
    """)
    connection._commit()
    #logger.info("Deleting extraneous cities...")
    #metro = get_metro()
    #cities = [l.name.upper() for l in Location.objects.filter(location_type__slug=metro['city_location_type']).exclude(location_type__name__startswith='Unknown')]
    #Street.objects.exclude(city__in=cities).delete()
    return Street.objects.all().count()

@timer
@transaction.commit_on_success
def populate_block_intersections(*args, **kwargs):
    logger.info("Starting to populate block_intersections")
    BlockIntersection.objects.all().delete()
    for block in Block.objects.all():
        logger.debug('Calculating the blocks that intersect %s' % block)
        for iblock, intersection_pt in intersecting_blocks(block):
            BlockIntersection.objects.get_or_create(
                block=block,
                intersecting_block=iblock,
                defaults={'location': intersection_pt}
            )
    return BlockIntersection.objects.all().count()

@timer
@transaction.commit_on_success
def populate_intersections(*args, **kwargs):
    # On average, there are 2.3 blocks per intersection. So for
    # example in the case of Chicago, where there are 788,496 blocks,
    # we'd expect to see approximately 340,000 intersections
    Intersection.objects.all().delete()
    logger.info("Starting to populate intersections")
    metro = get_metro()
    zipcodes = Location.objects.filter(location_type__name__istartswith="zip").exclude(name__startswith='Unknown')
    def lookup_zipcode(pt):
        for zipcode in zipcodes:
            if zipcode.location.contains(pt):
                return zipcode
    intersections_seen = {}
    for i in Intersection.objects.all():
        intersections_seen[i.pretty_name] = i.id
        intersections_seen[i.reverse_pretty_name()] = i.id
    for bi in BlockIntersection.objects.iterator():
        street_name = make_dir_street_name(bi.block)
        i_street_name = make_dir_street_name(bi.intersecting_block)
        # This tuple enables us to skip over intersections
        # we've already seen. Since intersections are
        # symmetrical---eg., "N. Kimball Ave. & W. Diversey
        # Ave." == "W. Diversey Ave. & N. Kimball Ave."---we
        # use both orderings.
        seen_intersection = (u"%s & %s" % (street_name, i_street_name),
                             u"%s & %s" % (i_street_name, street_name))
        if seen_intersection[0] not in intersections_seen and \
           seen_intersection[1] not in intersections_seen:
            if bi.block.left_city != bi.block.right_city:
                # If we have Locations representing cities,
                # find one that contains this bi's center.
                from ebpub.db.models import get_city_locations
                overlapping_cities = get_city_locations().filter(location__contains=bi.location)
                if overlapping_cities:
                    city = overlapping_cities[0].name.upper()
                else:
                    city = metro['city_name'].upper()
            else:
                city = bi.block.left_city
            if bi.block.left_state != bi.block.right_state:
                state = metro['state'].upper()
            else:
                state = bi.block.left_state
            if (bi.block.left_zip != bi.block.right_zip or \
                bi.intersecting_block.left_zip != bi.intersecting_block.right_zip) or \
               (bi.block.left_zip != bi.intersecting_block.left_zip):
                zipcode_obj = lookup_zipcode(bi.location)
                if zipcode_obj:
                    zipcode = zipcode_obj.name
                else:
                    zipcode = bi.block.left_zip
            else:
                zipcode = bi.block.left_zip
            intersection = intersection_from_blocks(bi.block, bi.intersecting_block, bi.location, city, state, zipcode)
            intersection.save()
            logging.debug("Created intersection %s" % intersection)
            bi.intersection = intersection
            bi.save()
            intersections_seen[seen_intersection[0]] = intersection.id
            intersections_seen[seen_intersection[1]] = intersection.id
        else:
            if not bi.intersection:
                bi.intersection_id = intersections_seen[seen_intersection[0]]
                bi.save()
            logger.debug("Already seen intersection %s" % " / ".join(seen_intersection))
    logger.info("Finished populating intersections")
    total = Intersection.objects.all().count()
    if not total:
        logger.warn("No intersections created, maybe you forgot to do populate_block_intersections first?")

LOG_VERBOSITY = (logging.CRITICAL,
                 logging.ERROR,
                 logging.WARNING,
                 logging.INFO,
                 logging.DEBUG,
                 logging.NOTSET)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    valid_actions = {'streets': populate_streets,
                     'block_intersections': populate_block_intersections,
                     'intersections': populate_intersections,
                     }
    parser = optparse.OptionParser('Usage: %%prog [opts] {%s}' % \
                                   '|'.join(valid_actions.keys()),
                                   description=__doc__)
    parser.add_option('-v', '--verbose', action='count', dest='verbosity',
                      default=0, help='verbosity, add more -v to be more verbose')

    opts, args = parser.parse_args(argv)
    if len(args) != 1 or args[0] not in valid_actions:
        parser.error('must supply an valid action, one of: %r' % \
                     valid_actions.keys())

    if not logger.handlers:
        verbosity = min(opts.verbosity, len(LOG_VERBOSITY) -1)
        level = LOG_VERBOSITY[verbosity]
        format = "%(asctime)-15s %(levelname)-8s %(message)s"
        basicConfig = logging.basicConfig
        try:
            if __name__ == '__main__':
                import fabulous.logs
                basicConfig = fabulous.logs.basicConfig
        except ImportError:
            pass
        basicConfig(level=level, format=format)


    # Call the action
    count = valid_actions[args[0]](**opts.__dict__)
    if count is not None:
        print "%s: created: %d" % (args[0], count)

if __name__ == '__main__':
    sys.exit(main())

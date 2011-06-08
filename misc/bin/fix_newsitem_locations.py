#   Copyright 2011 OpenPlans, and contributors
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

from ebpub.db.models import NewsItem
from ebpub.utils.geodjango import get_metro_bbox, intersects_metro_bbox
from django.contrib.gis.geos import Point

def main(dry_run=True):
    items_outside = list(NewsItem.objects.exclude(location__intersects=get_metro_bbox()))
    print "Items outside bounds: %s" % len(items_outside)
    for item in items_outside:
        fix_newsitem_coords(item, dry_run)
    items_no_loc_name = list(NewsItem.objects.filter(location_name=''))
    print "Items with no location name: %s" % len(items_no_loc_name)
    for item in items_no_loc_name:
        fix_newsitem_loc_name(item, dry_run)


def fix_newsitem_loc_name(item, dry_run=True):
    # Fall back to reverse-geocoding.
    from ebpub.geocoder import reverse
    fixed = False
    try:
        block, distance = reverse.reverse_geocode(item.location)
        print " Reverse-geocoded point to %r" % block.pretty_name
        item.location_name = block.pretty_name
        item.block = block
        fixed = True
    except reverse.ReverseGeocodeError:
        print " Failed to reverse geocode %s for %s" % (item.location.wkt, item)
        item.location_name = u''
    if fixed and not dry_run:
        print "Saving %s" % item
        item.save()

def fix_newsitem_coords(item, dry_run=True):
    """
    Try to fix a (presumably bad) NewsItem geometry by reversing its
    coordinates, or reverse-geocoding if it has a location name; use
    whatever works.

    If dry_run=False, the item will be saved.
    """
    if item.location is not None:
        loc = item.location.centroid
        print "Found %r outside bounds at %s, %s" % (item.title,
                                                 loc.x, loc.y)
    else:
        loc = None
        print "NO location on %s" % item
    fixed = False
    if item.location_name:
        from ebpub.geocoder import SmartGeocoder, AmbiguousResult
        try:
            result = SmartGeocoder().geocode(item.location_name)
        except AmbiguousResult, e:
            # Just pick one.
            result = e.choices[0]
        except:
            result = None
        if result and intersects_metro_bbox(result['point']):
            print "Fixing %r by geocoding %r" % (item.title, item.location_name)
            item.location = result['point']
            item.block = result['block']
            fixed = True

    if loc and not fixed:
        newloc = Point(loc.y, loc.x)
        if intersects_metro_bbox(newloc):
            print "Fixing %r by flipping bounds" % item.title
            item.location = newloc
            fixed = True

    if not dry_run:
        if fixed:
            print "saving %s" % item
            item.save()
        else:
            print "Can't fix %s, deleting" % item
            item.delete()

if __name__ == '__main__':
    import sys
    dry_run = int(sys.argv[1])
    main(dry_run=dry_run)

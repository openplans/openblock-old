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

from ebpub.db.models import NewsItem, Attribute, Lookup, Schema


def delete(schema=None, do_delete=False):
    """
    Delete all NewsItems of a given Schema.

    By default, does a dry run and just prints;
    """
    schema = Schema.objects.get(slug=schema)
    qs = NewsItem.objects.filter(schema=schema).order_by('-id')
    if not do_delete:
        print "Would delete %d for schema %s ..." % (qs.count(), schema)
        print qs
    else:
        print "Deleting %d for schema %s ..." % (qs.count(), schema)
        qs.delete()
        print "Deleted."
        qs = Attribute.objects.filter(schema=schema).order_by('-id')
        print "Deleting %d attributes for schema %s ..." % (qs.count(), schema)
        qs.delete()
        print "Deleted."
        qs = Lookup.objects.filter(schema_field__schema=schema).order_by('-id')
        print "Deleting %d lookups for schema %s ..." % (qs.count(), schema)
        qs.delete()
        print "Deleted."


def main():
    import sys
    argv = sys.argv[1:]
    from optparse import OptionParser
    optparser = OptionParser()
    optparser.add_option('-d', '--dry-run', action='store_true')
    opts, args = optparser.parse_args(argv)
    schema_slug = args[0]
    delete(schema_slug, do_delete=not opts.dry_run)

if __name__ == "__main__":
    main()

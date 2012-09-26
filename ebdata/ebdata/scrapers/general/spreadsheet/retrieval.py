#   Copyright 2012 OpenPlans and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.


from cStringIO import StringIO
from ebdata.parsing import unicodecsv
from ebdata.parsing import excel
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.retrieval.scrapers.list_detail import SkipRecord
from ebpub.utils.dates import now, today
from ebpub.db.models import Lookup
import mimetypes
import re
import urllib2


def get_default_unique_field_names():
    """
    Which fields of NewsItem uniquely identify a particular NewsItem.
    """
    # Don't use dates
    blacklist = ('item_date', 'pub_date', 'id', 'schema', 'last_modification',
                 )
    from ebpub.db.models import NewsItem
    return sorted(
        [f.name for f in NewsItem._meta.fields if f.name not in blacklist]
        )

def get_dictreader(items_sheet, items_type='text/csv', map_sheet=None, map_type='text/csv'):
    """
    Given one or two spreadsheets as File objects, or bytestrings,
    return a DictReader that can be used to retrieve rows from
    ``items_sheet``.

    If no ``map_sheet`` is passed, assume that ``items_sheet`` includes headers,
    and return a normal DictReader.

    If ``map_sheet`` is passed, assume it describes which columns from
    ``items_sheet`` should be used for which fields of the output
    dicts.

    Examples follow. First with no map_sheet::

      >>> rows = [['attendee', 'unused', 'event'],
      ...         ['Bob', 'xyz', 'film premiere'],
      ...         ['Carol', 'pdq', 'workshop']]
      >>> csv = '\\n'.join([','.join(map(str, r)) for r in rows])
      >>> reader = get_dictreader(csv)
      >>> import pprint
      >>> pprint.pprint(list(reader))
      [{'attendee': u'Bob', 'event': u'film premiere', 'unused': u'xyz'},
       {'attendee': u'Carol', 'event': u'workshop', 'unused': u'pdq'}]

    If ``map_sheet`` is passed and has *two* rows, then each column
    desribes an old key and a new key for use in re-mapping the output
    dictionaries from items_sheet. Each key of the mapping (from row 1
    of map_sheet) represents the original key from the ``items_sheet``
    header; each value (from row 2 of map_sheet) represents a new key
    for use in the output dict.  Columns whose headers do not appear
    in ``mapping`` are dropped from the output. Example::

      >>> rows = [['attendee', 'unused', 'event'],
      ...         ['Bob', 'xyz', 'film premiere'],
      ...         ['Carol', 'pdq', 'workshop']]
      >>> csv = '\\n'.join([','.join(map(str, r)) for r in rows])
      >>> mapping = {'event': 'where', 'attendee': 'who'}
      >>> map_sheet = 'attendee,event\\nwho,where'
      >>> reader = get_dictreader(csv, map_sheet=map_sheet)
      >>> reader.mapping == mapping
      True
      >>> pprint.pprint(list(reader))
      [{u'where': u'film premiere', u'who': u'Bob'},
       {u'where': u'workshop', u'who': u'Carol'}]


    If ``map_sheet`` is passed and has **one** row, then assume
    ``items_sheet`` has no header; use the row from ``map_sheet`` as a list of
    fieldnames to set in each output dict. The index of each fieldname
    determines the column number of items_sheet that contains that
    field.::

      >>> fieldnames = ['animal', 'color', 'number']
      >>> map_sheet = ','.join(fieldnames)
      >>> rows = [['cat', 'purple', 3], ['dog', 'white', 0], ['bird', 'yellow']]
      >>> csv = '\\n'.join([','.join(map(str, r)) for r in rows])
      >>> reader = get_dictreader(csv, map_sheet=map_sheet)
      >>> pprint.pprint(list(reader))
      [{'animal': u'cat', 'color': u'purple', 'number': u'3'},
       {'animal': u'dog', 'color': u'white', 'number': u'0'},
       {'animal': u'bird', 'color': u'yellow'}]

    If ``map_sheet`` has more than two rows, it's an error::

      >>> map_sheet = 'one,two,three\\nfour,five,six\\n7,8,9\\n'
      >>> get_dictreader(csv, map_sheet=map_sheet) # doctest: +ELLIPSIS
      Traceback (most recent call last):
      ...
      ValueError: Too many rows...

    A map_sheet with zero rows is the same as not passing one at all:

      >>> reader1 = get_dictreader(csv)
      >>> reader2 = get_dictreader(csv, map_sheet='\\n')
      >>> list(reader2) == list(reader1)
      True

    The sheets can be file objects:

      >>> import StringIO
      >>> reader3 = get_dictreader(csv)
      >>> reader4 = get_dictreader(StringIO.StringIO(csv))
      >>> list(reader3) == list(reader4)
      True

    You can pass an old-style Excel spreadsheet (we should probably test with a real one):

      >>> import mock
      >>> with mock.patch('ebdata.scrapers.general.spreadsheet.retrieval.excel.ExcelDictReader') as mock_factory:
      ...     mock_factory.return_value = 'yup it was excel'
      ...     print get_dictreader("blah", items_type='application/vnd.ms-excel')
      yup it was excel

    """

    factory_map = {
        'text/plain': unicodecsv.UnicodeDictReader,
        'text/csv': unicodecsv.UnicodeDictReader,
        'application/vnd.ms-excel': excel.ExcelDictReader,
        'application/msexcel': excel.ExcelDictReader,
    }
    # TODO: use http://packages.python.org/openpyxl/ to handle new-style
    # xslx files. Would require a DictReader-like facade to be written.
    reader_factory = factory_map.get(items_type, unicodecsv.UnicodeDictReader)
    map_reader_factory = factory_map.get(map_type, unicodecsv.UnicodeDictReader)

    if isinstance(items_sheet, basestring):
        items_sheet = StringIO(items_sheet)
    if map_sheet is None:
        # Assume items_sheet is properly set up to just use with a DictReader.
        return reader_factory(items_sheet)
    if isinstance(map_sheet, basestring):
        map_sheet = StringIO(map_sheet)
    mapping = map_reader_factory(map_sheet)
    map_rows = [row for row in list(mapping) if row]
    if len(map_rows) == 0:
        return reader_factory(items_sheet, fieldnames=mapping.fieldnames)
    elif len(map_rows) == 1:
        return RemappingDictReader(items_sheet, map_rows[0], reader_factory)
    else:
        raise ValueError("Too many rows in map_sheet, you can only have 1 or 2")


class RemappingDictReader(object):

    """Wraps another Reader instance and remaps its column names
    according to the ``mapping`` argument.
    """

    def __init__(self, f, mapping, readerclass, **kwargs):
        self.mapping = mapping
        self.reader = readerclass(f, **kwargs)

    def __iter__(self):
        for row in self.reader:
            result = {}
            for oldkey, newkey in self.mapping.items():
                result[newkey] = row.get(oldkey)
            yield result


class SpreadsheetScraper(NewsItemListDetailScraper):
    """General-purpose CSV file scraper.

    You should set ``unique_fields`` to a list of the fields that can
    be used to uniquely identify a row in the input file.
    (TODO: this currently doesn't support Attributes, only core
    NewsItem fields.)

    If you don't set ``unique_fields``, the default is to assume
    that all non-date fields must be unique.
    """

    has_detail = False
    schema_slugs = None
    unique_fields = ()
    get_location_name_from_all_fields = True

    def __init__(self, items_sheet_file, map_sheet_file, *args, **kwargs):
        self.schema_slugs = [kwargs.pop('schema_slug', None)]
        self.unique_fields = kwargs.pop('unique_fields', self.unique_fields)

        super(SpreadsheetScraper, self).__init__(*args, **kwargs)
        self.items_sheet_file = items_sheet_file
        if items_sheet_file:
            self.items_sheet, self.items_type = open_url(items_sheet_file)
            self.items_sheet = self.items_sheet.read()
        else:
            # In this case you'll have to manually set it after __init__.
            self.items_sheet = self.items_type = None
        if map_sheet_file:
            self.map_sheet, self.map_type = open_url(map_sheet_file)
            self.map_sheet = self.map_sheet.read()
        else:
            self.map_sheet = self.map_type = None

    def list_pages(self):
        return [self.items_sheet]

    def parse_list(self, page):
        reader = get_dictreader(page, items_type=self.items_type,
                                map_sheet=self.map_sheet,
                                map_type=self.map_type)
        # DictReaders are iterable and yield dicts, so, we're done.
        return reader


    def existing_record(self, record):
        """
        Uses the fields named in self.unique_fields.
        If self.unique_fields isn't set, use all non-date core fields
        of NewsItem.
        """
        from ebpub.db.models import NewsItem
        query_args = {}
        unique_fields = self.unique_fields or get_default_unique_field_names()
        for field in unique_fields:
            arg = record.get(field)
            if arg:
                query_args[field] = arg

        if not query_args:
            return None
        qs = list(NewsItem.objects.filter(schema__id=self.schema.id, **query_args))
        if not qs:
            return None
        if len(qs) > 1:
            self.logger.warn("Multiple entries matched args %r. Expected unique! Using first one." % str(query_args))
        return qs[0]


    def clean_list_record(self, list_record):
        """
        Given a dict, prepare it for saving as a newsitem.
        Result will be a dictionary of anything from list_record
        that looks like a known field of the NewsItem model.

        Anything that looks like a known SchemaField of the item's Schema
        will be set as an item in an 'attributes' sub-dictionary.

        Unrecognized keys will be ignored (and logged).

        Locations are found heuristically:
         - If there's a 'location' key, try to split the value into (lat, lon) points
         - If there's keys like 'latitude'/'lat' and 'longitude'/'lon'/'long'/'lng', use those
         - If there's a 'location_name', geocode if needed
         - If there's no 'location_name', reverse-geocode if possible

        """
        from ebpub.db.models import NewsItem
        fieldnames = [f.name for f in NewsItem._meta.fields]
        core_fields = {}
        from ebdata.retrieval.utils import get_point
        if 'location' in list_record:
            # If there's a comma- or space-separated location in the
            # orginal, this gives us a way to use it by mapping it to
            # "location"
            try:
                lat, lon = re.split(r'[\s,]+', str(list_record.pop('location')))
                list_record.setdefault('lat', lat)
                list_record.setdefault('lon', lon)
            except ValueError:
                pass
        # Now try all the field names recognized by get_point(), eg
        # lat, latitude, lon, long, lng, georss_point, etc.
        point = get_point(list_record)
        for fieldname in fieldnames:
            if fieldname in list_record:
                # TODO: coerce types? Or maybe Django's implicit conversion is OK.
                core_fields[fieldname] = list_record.pop(fieldname)

        # Try to ensure we have both point and location_name;
        # fall back to address extraction from *all* fields.
        address_text = core_fields.get('location_name')
        if self.get_location_name_from_all_fields and not address_text:
            address_text = '\n'.join([unicode(s) for s in list_record.values()])
        point, location_name = self.geocode_if_needed(point, address_text)
        core_fields['location'] = point
        core_fields['location_name'] = location_name

        # Attributes.
        attributes = list_record.get('attributes', {})
        schemafields = self.schema.schemafield_set.all()
        for sf in schemafields:
            if sf.name in list_record:
                # TODO: coerce types? Or maybe Django's implicit conversion is OK.
                value = list_record.pop(sf.name)
                if sf.is_many_to_many_lookup():
                    # Passed value needs to be a list of strings.
                    if isinstance(value, basestring):
                        value = [value]
                    lookups = [
                        Lookup.objects.get_or_create_lookup(
                            sf, name=v, code=v, make_text_slug=False
                        )
                        for v in value]
                    value = ','.join([str(lookup.id) for lookup in lookups])

                elif sf.is_lookup:
                    # Need an int id.
                    value = unicode(value)
                    value = Lookup.objects.get_or_create_lookup(
                        sf, name=value, code=value, make_text_slug=False)
                    value = value.id
                else:
                    # TODO: handle other types?
                    value = unicode(value)
                attributes[sf.name] = value
        core_fields['attributes'] = attributes
        if len(list_record):
            self.logger.debug("Unused stuff from list_record: %s" % list_record)
        return core_fields

    def save(self, old_record, list_record, detail_record):
        attributes = list_record.pop('attributes', {})
        list_record.setdefault('schema', self.schema.id)
        if not old_record:
            list_record.setdefault('item_date', today())
            list_record.setdefault('pub_date', now())
        from ebpub.db.forms import NewsItemForm
        form = NewsItemForm(list_record, instance=old_record)
        if form.is_valid():
            return self.create_or_update(old_record, attributes,
                                         **form.cleaned_data)
        else:
            self.logger.info("Skipping due to validation failures:")
            for key, val in form.errors.items():
                self.logger.info("%s: %s" % (key, val.as_text()))
            raise SkipRecord(form.errors)


    def update(self, *args, **kwargs):
        self.logger.info("Retrieving %s" % self.items_sheet_file)
        result = super(SpreadsheetScraper, self).update(*args, **kwargs)
        self.logger.info("Added: %d; Updated: %d; Skipped: %d" %
                         (self.num_added, self.num_changed, self.num_skipped))
        return result


def open_url(url):
    """maybe it's a URI, maybe a local file.
    Either way, return a file-like object and a mimetype.
    """
    try:
        return (file(url), mimetypes.guess_type(url)[0])
    except IOError:
        return (urllib2.urlopen(url), mimetypes.guess_type(url)[0])


def main(argv=None):
    import sys
    if argv is None:
        argv = sys.argv[1:]
    from optparse import OptionParser
    usage = "usage: %prog [options] <spreadsheet> [<mapping spreadsheet>]"
    usage += "\n\nSpreadsheet arguments can be local files or URLs."
    usage += "\n\nSee http://openblockproject.org/docs/packages/ebdata.html#spreadsheets-scrapers-general-spreadsheet for more."
    parser = OptionParser(usage=usage)

    parser.add_option(
        "--schema", help="slug of news item type to create when scraping",
        default="local-news"
        )

    parser.add_option(
        "--unique-fields", help="Which NewsItem fields identify a unique record in this data source. Comma-separated, eg. --unique-fields='url,location_name,title",
        action="store", default=None
        )

    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    add_verbosity_options(parser)

    options, args = parser.parse_args(argv)
    if len(args) >= 1:
        items_sheet = args[0]
        if len(args) >= 2:
            map_sheet = args[1]
        else:
            map_sheet = None
    else:
        parser.print_usage()
        sys.exit(0)

    if options.unique_fields:
        unique_fields = [s.strip() for s in options.unique_fields.split(',')]
    else:
        unique_fields = []
    scraper = SpreadsheetScraper(items_sheet, map_sheet,
                                 schema_slug=options.schema,
                                 unique_fields=unique_fields)
    setup_logging_from_opts(options, scraper.logger)
    scraper.update()


if __name__ == '__main__':
    main()

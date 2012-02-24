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
from ebdata.retrieval.scrapers.list_detail import ListDetailScraper
from ebpub.db.models import NewsItem
from ebpub.utils.dates import today, now

def get_dictreader(items_csv, map_csv=None):
    """
    Given one or two spreadsheets, return a DictReader that can be
    used to retrieve rows from ``items_csv``.

    If no ``map_csv`` is passed, assume that ``items_csv`` includes headers,
    and return a normal DictReader.

    If ``map_csv`` is passed, assume it describes which columns from
    ``items_csv`` should be used for which fields of the output
    dicts.

    Examples follow. First with no map_csv::

      >>> rows = [['attendee', 'unused', 'event'],
      ...         ['Bob', 'xyz', 'film premiere'],
      ...         ['Carol', 'pdq', 'workshop']]
      >>> csv = '\\n'.join([','.join(map(str, r)) for r in rows])
      >>> reader = get_dictreader(csv)
      >>> import pprint
      >>> pprint.pprint(list(reader))
      [{'attendee': u'Bob', 'event': u'film premiere', 'unused': u'xyz'},
       {'attendee': u'Carol', 'event': u'workshop', 'unused': u'pdq'}]

    If ``map_csv`` is passed and has *two* rows, then each column
    desribes an old key and a new key for use in re-mapping the output
    dictionaries from items_csv. Each key of the mapping (from row 1
    of map_csv) represents the original key from the ``items_csv``
    header; each value (from row 2 of map_csv) represents a new key
    for use in the output dict.  Columns whose headers do not appear
    in ``mapping`` are dropped from the output. Example::

      >>> rows = [['attendee', 'unused', 'event'],
      ...         ['Bob', 'xyz', 'film premiere'],
      ...         ['Carol', 'pdq', 'workshop']]
      >>> csv = '\\n'.join([','.join(map(str, r)) for r in rows])
      >>> mapping = {'event': 'where', 'attendee': 'who'}
      >>> map_csv = 'attendee,event\\nwho,where'
      >>> reader = get_dictreader(csv, map_csv)
      >>> reader.mapping == mapping
      True
      >>> pprint.pprint(list(reader))
      [{u'where': u'film premiere', u'who': u'Bob'},
       {u'where': u'workshop', u'who': u'Carol'}]


    If ``map_csv`` is passed and has **one** row, then assume
    ``item_csv`` has no header; use the row from ``map_csv`` as a list of
    fieldnames to set in each output dict. The index of each fieldname
    determines the column number of items_csv that contains that
    field.::

      >>> fieldnames = ['animal', 'color', 'number']
      >>> map_csv = ','.join(fieldnames)
      >>> rows = [['cat', 'purple', 3], ['dog', 'white', 0], ['bird', 'yellow']]
      >>> csv = '\\n'.join([','.join(map(str, r)) for r in rows])
      >>> reader = get_dictreader(csv, map_csv)
      >>> pprint.pprint(list(reader))
      [{'animal': u'cat', 'color': u'purple', 'number': u'3'},
       {'animal': u'dog', 'color': u'white', 'number': u'0'},
       {'animal': u'bird', 'color': u'yellow'}]

    If ``map_csv`` has more than two rows, it's an error::

      >>> map_csv = 'one,two,three\\nfour,five,six\\n7,8,9\\n'
      >>> get_dictreader(csv, map_csv) # doctest: +ELLIPSIS
      Traceback (most recent call last):
      ...
      ValueError: Too many rows...

    A map_csv with zero rows is the same as not passing one at all:

      >>> reader1 = get_dictreader(csv)
      >>> reader2 = get_dictreader(csv, '\\n')
      >>> list(reader2) == list(reader1)
      True

    """

    if isinstance(items_csv, basestring):
        items_csv = StringIO(items_csv)
    if map_csv is None:
        # Assume items_csv is properly set up to just use with a DictReader.
        return unicodecsv.UnicodeDictReader(items_csv)
    if isinstance(map_csv, basestring):
        map_csv = StringIO(map_csv)
    mapping = unicodecsv.UnicodeDictReader(map_csv)
    map_rows = list(mapping)
    if len(map_rows) == 0:
        return unicodecsv.UnicodeDictReader(items_csv, fieldnames=mapping.fieldnames)
    elif len(map_rows) == 1:
        return RemappingDictReader(items_csv, map_rows[0])
    else:
        raise ValueError("Too many rows in map_csv, you can only have 1 or 2")


class RemappingDictReader(unicodecsv.UnicodeDictReader):
    def __init__(self, f, mapping, **kwargs):
        self.mapping = mapping
        super(RemappingDictReader, self).__init__(f, **kwargs)

    def next(self):
        row = super(RemappingDictReader, self).next()
        result = {}
        for oldkey, newkey in self.mapping.items():
            result[newkey] = row.get(oldkey)
        return result


class CsvListDetailScraper(ListDetailScraper):
    has_detail = False

    def __init__(self, items_csv, map_csv, *args, **kwargs):
        super(CsvListDetailScraper, self).__init__(*args, **kwargs)
        self.items_csv = items_csv
        self.map_csv = map_csv

    def list_pages(self):
        pass

    def clean_list_record(self, list_record):
        """
        Given a dict, prepare it for saving as a newsitem.
        Result will be a dictionary of anything from list_record
        that looks like a known field of the NewsItem model.
        Anything that looks like a known SchemaField of the item's Schema
        will be set as an 'attributes' sub-dictionary.

        Unrecognized keys will be ignored (and logged).
        """
        fieldnames = [f.name for f in NewsItem._meta.fields]
        core_fields = {}
        from ebdata.retrieval.utils import get_point
        point = get_point(list_record)
        for fieldname in fieldnames:
            if fieldname in list_record:
                # TODO: coerce types
                core_fields[fieldname] = list_record.pop(fieldname)
        # TODO: parse addresses out of... what?
        point, location_name = self.geocode_if_needed(
            point, core_fields.get('location_name'))
        core_fields['location'] = point
        core_fields['location_name'] = location_name

        # Attributes.
        attributes = {}
        schemafields = self.schema.schemafield_set.all()
        for sf in schemafields:
            if sf.name in list_record:
                # TODO: coerce types
                attributes[sf.name] = list_record.pop(sf.name)
        core_fields['attributes'] = attributes
        core_fields.setdefault('schema', self.schema) # XXX
        if len(list_record):
            self.logger.debug("Unused stuff from list_record: %s" % list_record)
        return core_fields

    def save(self, old_record, list_record, detail_record):
        attributes = list_record.pop('attributes', {})
        list_record.setdefault('schema', self.schema.id)
        list_record.setdefault('item_date', today())
        list_record.setdefault('pub_date', now())
        from ebpub.db.forms import NewsItemForm
        form = NewsItemForm(list_record, instance=old_record)
        if form.is_valid():
            return self.create_or_update(old_record, attributes,
                                         **form.cleaned_data)
        else:
            # XXX TODO: does anything check return value of save()?
            # What to do w/ errors?
            return {'errors': form.errors}

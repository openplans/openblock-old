#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
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
#

"""
Support for reading CSV as Unicode objects.

This module is necessary because Python's csv library doesn't support reading
Unicode strings.  STILL true as of Python 2.7.
"""

# This code is derived from code in the Python documentation:
# http://www.python.org/doc/2.5.2/lib/csv-examples.html
# The changes we've made are to implement a DictReader instead of a normal
# Reader.
# 
# The code is Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Python Software
# Foundation; All Rights Reserved
# See the full license at http://www.python.org/psf/license/

import csv
import codecs

class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8.
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')


class UnicodeReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding. Results will always be Unicode
    objects instead of bytestrings.
    """

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwargs):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwargs)

    def next(self):
        row = self.reader.next()
        row = [unicode(s, 'utf-8') for s in row]
        return row

    def __iter__(self):
        return self


class UnicodeDictReader(UnicodeReader):
    """
    A CSV dict reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding. Results will always be Unicode
    objects instead of bytestrings.
    """

    def __init__(self, f, fieldnames=None, dialect=csv.excel, encoding='utf-8', **kwargs):
        super(UnicodeDictReader, self).__init__(
            f, dialect=dialect, encoding=encoding, **kwargs)
        if fieldnames:
            self.fieldnames = fieldnames
        else:
            throwaway_reader = csv.DictReader(f)
            self.fieldnames = throwaway_reader.fieldnames
            del(throwaway_reader)
            # Note we are relying on a side effect here:
            # csv.DictReader(f) advanced f to the next line.

    def next(self):
        row = super(UnicodeDictReader, self).next()
        return dict(zip(self.fieldnames, row))

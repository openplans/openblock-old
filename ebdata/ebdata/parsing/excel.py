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
Utilities for reading Microsoft Excel files.

Only handles old-style excel files.

TODO: use http://packages.python.org/openpyxl/ to handle new-style
xslx files.
"""

import xlrd
import datetime

class ExcelDictReader(object):
    """
    Provides an API that lets you iterate over every row in an Excel worksheet,
    much like csv.DictReader. This assumes that the worksheet is a simple table
    with a single header row at the top.

    header_row_num is the zero-indexed row number of the headers. (Note that
    you can specify the headers manually by using the "custom_headers"
    argument.)

    start_row_num is the zero-indexed row number of where the data starts.

    use_last_header_if_duplicate, either True or False, dictates the behavior
    to use in the case of duplicate column headers. If True, then the *last*
    column's value will be used. If False, then the *first* column's value will
    be used. Note that there's no way to access the other column, either way.

    custom_headers, if given, will be used instead of the values in
    header_row_num. If you provide custom_headers, the value of header_row_num
    will be ignored.

    Example usage::

        reader = ExcelDictReader('/path/to/my.xls', 0, 0, 1)
        for row in reader:
            print row

    This yields dictionaries like::

        {'header1': 'value1', 'header2': 'value2'}

    The first argument can be either a path, or an open file-like object.
    """
    def __init__(self, filename, sheet_index=0, header_row_num=0, start_row_num=0,
            use_last_header_if_duplicate=True, custom_headers=None):

        if hasattr(filename, 'read'):
            self.workbook = xlrd.open_workbook(file_contents=filename.read())
        else:
            self.workbook = xlrd.open_workbook(filename)
        self.sheet_index = sheet_index
        if not start_row_num and not custom_headers:
            # Like csv.DictReader, assume first row is headers.
            start_row_num = header_row_num + 1
        self.header_row, self.start_row = header_row_num, start_row_num
        self.use_last_header_if_duplicate = use_last_header_if_duplicate
        self.custom_headers = custom_headers
        self._fieldnames = custom_headers

    # For consistency with csv.DictReader
    @property
    def fieldnames(self):
        if self._fieldnames is None:
            worksheet = self.workbook.sheet_by_index(self.sheet_index)
            self._fieldnames = [v.value.strip() for v in worksheet.row(self.header_row)]
        return self._fieldnames

    def __iter__(self):
        worksheet = self.workbook.sheet_by_index(self.sheet_index)
        headers = self.fieldnames
        for row_num in xrange(self.start_row, worksheet.nrows):
            data_dict = {}
            for i, cell in enumerate(worksheet.row(row_num)):
                value = cell.value

                # Clean up the value. The xlrd library doesn't convert date
                # values to Python objects automatically, so we have to do that
                # here. Also, strip whitespace from any text field.
                # cell.ctype is documented here:
                # http://www.lexicon.net/sjmachin/xlrd.html#xlrd.Cell-class
                if cell.ctype == 3:
                    try:
                        value = datetime.datetime(*xlrd.xldate_as_tuple(value, self.workbook.datemode))
                    except ValueError:
                        # The datetime module raises ValueError for invalid
                        # dates, like the year 0. Rather than skipping the
                        # value (which would lose data), we just keep it as
                        # a string.
                        pass
                elif cell.ctype == 1:
                    value = value.strip()

                # Only append the value to the dictionary if 
                if self.use_last_header_if_duplicate or headers[i] not in data_dict:
                    data_dict[headers[i]] = value

            yield data_dict

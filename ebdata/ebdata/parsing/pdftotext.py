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
Utilities for reading data from PDF files.

These require the pdftotext binary, available in the Xpdf package:
    http://www.foolabs.com/xpdf/download.html
"""

import os

PDFTOTEXT_BINARY = 'pdftotext'

def pdf_to_text(filename, keep_layout=True, raw=False):
    """
    Returns the text of the PDF with the given filename on the local filesystem.
    """
    if keep_layout and raw:
        raise ValueError('The "keep_layout" and "raw" arguments may not be used together')
    options = []
    if keep_layout:
        options.append('-layout')
    if raw:
        options.append('-raw')
    cmd = "%s %s '%s' -" % (PDFTOTEXT_BINARY, ' '.join(options), filename)
    return os.popen(cmd).read()

def pdfstring_to_text(pdf_string, keep_layout=True, raw=False):
    """
    Returns the text of the given PDF (provided as a string).
    """
    import os
    from tempfile import mkstemp
    fd, name = mkstemp()
    fp = os.fdopen(fd, 'wb')
    fp.write(pdf_string)
    fp.close()
    try:
        result = pdf_to_text(name, keep_layout, raw)
    finally:
        os.unlink(name)
    return result

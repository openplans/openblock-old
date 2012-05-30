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

'''
The parsing package contains helpers for reading different file types.

The :py:mod:`dbf`, :py:mod:`excel`, :py:mod:`mdb`, and
:py:mod:`unicodecsv` modules are for reading stuctured data, and
generally follow the python csv reader api. See the code for more
details on how to use them.

The pdf module is for converting pdf to text, and requires Xpdf.
http://www.foolabs.com/xpdf/download.html
'''

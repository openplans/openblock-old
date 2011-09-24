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

import datetime
import time

def daterange(d1, d2):
    "Iterator that returns every date between d1 and d2, inclusive."
    current = d1
    while current <= d2:
        yield current
        current += datetime.timedelta(days=1)

def parse_date(value, format, return_datetime=False):
    """
    Equivalent to time.strptime, but it returns a datetime.date or
    datetime.datetime object instead of a struct_time object.

    If you pass a date or datetime instance, you get it back.

    Returns None if the value evaluates to False.

    >>> parse_date(None, '')
    >>> parse_date('', '')
    >>> parse_date('2000', '%Y')
    datetime.date(2000, 1, 1)
    >>> parse_date('2000', '%Y', True) # doctest: +ELLIPSIS
    datetime.datetime(2000, 1, 1, 0, 0, 0, ...)
    >>> parse_date(datetime.date(2000, 1, 1), '%Y')
    datetime.date(2000, 1, 1)

    """
    # See http://docs.python.org/library/time.html#time.strftime
    idx = return_datetime and 7 or 3
    func = return_datetime and datetime.datetime or datetime.date
    if isinstance(value, func):
        return value
    if value:
        return func(*time.strptime(value, format)[:idx])
    return None

def parse_time(value, format):
    """
    Equivalent to time.strptime, but it returns a datetime.time object.

    >>> parse_time('23:59:01', '%H:%M:%S')
    datetime.time(23, 59, 1)
    """
    return datetime.time(*time.strptime(value, format)[3:6])

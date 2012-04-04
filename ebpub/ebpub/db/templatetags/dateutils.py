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
Template tags for working with dates.
To use these, your template must include:

.. code-block:: html+django

   {% load dateutils %}

"""

from django import template
from ebpub.utils.dates import today
import calendar
import datetime

register = template.Library()

def days_in_month(value):
    """A filter.  Given a ``datetime.date`` or ``datetime.datetime`` object,
    returns the number of days in that month.

    Example:

    .. code-block:: html+django

      {{ some_date|days_in_month }}

    Example output::

      31

    Examples, in python:

    .. code-block:: python

      >>> import datetime
      >>> print days_in_month(datetime.date(2011, 8, 15))
      31
      >>> print days_in_month(datetime.datetime(2011, 8, 15, 0, 0))
      31
      >>> print days_in_month(datetime.date(2012, 2, 1))
      29
      >>> print days_in_month(datetime.date(2011, 2, 1))
      28
    """
    return calendar.monthrange(value.year, value.month)[1]
register.filter('days_in_month', days_in_month)

def friendlydate(value):
    """
    A filter that takes a date and includes 'Today' or 'Yesterday' if
    relevant, or the day of the week if it's within the past week,
    otherwise just the date.

    Example (in template):

    .. code-block:: html+django

      {% start_date|friendlydate %}

    Examples, in python:

    .. code-block:: python

      >>> import mock, datetime
      >>> with mock.patch('ebpub.db.templatetags.dateutils.today', lambda: datetime.date(2011, 8, 15)):
      ...     print friendlydate(datetime.date(2011, 8, 15))
      ...     print friendlydate(datetime.date(2011, 8, 16))
      ...     print friendlydate(datetime.date(2011, 8, 14))
      ...     print friendlydate(datetime.date(2011, 8, 13))
      ...     print friendlydate(datetime.date(2011, 8, 9))
      ...     print friendlydate(datetime.date(2011, 8, 8))
      ...
      Today August 15, 2011
      Tomorrow August 16, 2011
      Yesterday August 14, 2011
      Saturday August 13, 2011
      Tuesday August 9, 2011
      August 8, 2011
    """
    try: # Convert to a datetime.date, if it's a datetime.datetime.
        value = value.date()
    except AttributeError:
        pass
    # Using value.day because strftine('%d') is zero-padded and we don't want that.
    # TODO: parameterize format to allow i18n?
    formatted_date = value.strftime('%B ') + unicode(value.day) + value.strftime(', %Y')
    _today = today()
    if value == _today:
        return 'Today %s' % formatted_date
    elif value == _today - datetime.timedelta(1):
        return 'Yesterday %s' % formatted_date
    elif value == _today + datetime.timedelta(1):
        return 'Tomorrow %s' % formatted_date
    elif _today - value <= datetime.timedelta(6):
        return '%s %s' % (value.strftime('%A'), formatted_date)
    return formatted_date

register.filter('friendlydate', friendlydate)

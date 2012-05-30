#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of obdemo
#
#   obdemo is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   obdemo is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with obdemo.  If not, see <http://www.gnu.org/licenses/>.
#

"""
An alternate settings file that disables default logging config,
because a bug in django-background-task means that any existing
logging config overrides the command-line options.  See
https://github.com/lilspikey/django-background-task/issues/2
"""

from obdemo.settings import *


del(LOGGING)

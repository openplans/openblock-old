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
The templatemaker package contains utilities for detecting the actual content
given a set of html pages that were generated from a template. For instance,
templatemaker helps detect and extract the actual article from a page that
could also contain navigation links, ads, etc.

This is used internally by :py:mod:`ebdata.blobs`. It is not typically used
directly by scraper scripts.

'''

from hole import Hole
from template import Template, NoMatch


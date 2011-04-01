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

from django.conf import settings

# Needed so `manage.py test` can find these tests.
# Won't have the django-nose run-tests-twice problem unless
# these modules are named test*.py

#from .articletext import *
from .brain import *
from .clean import *
from .hole import *
from .htmlutils import *
from .listdiff import *
from .sst import *
from .template import *
from .textlist import *
from .webmining import *

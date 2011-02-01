#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebblog
#
#   ebblog is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebblog is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebblog.  If not, see <http://www.gnu.org/licenses/>.
#

import os

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/ebblog.db'
DATABASE_USER = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

ROOT_URLCONF = 'ebblog.urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'ebblog.blog',
)

TEMPLATE_DIRS = (
    os.path.normpath(os.path.join(os.path.dirname(__file__), 'templates')),
)

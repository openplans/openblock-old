#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebwiki
#
#   ebwiki is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebwiki is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebwiki.  If not, see <http://www.gnu.org/licenses/>.
#

import os

DEBUG = True

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_USER = ''
DATABASE_HOST = ''
DATABASE_NAME = 'wiki'

INSTALLED_APPS = (
    'ebwiki.wiki',
)

TEMPLATE_DIRS = (
    os.path.normpath(os.path.join(os.path.dirname(__file__), 'templates')),
)

ROOT_URLCONF = 'ebwiki.wiki.urls'

WIKI_DOC_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), 'media'))

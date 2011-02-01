#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebinternal
#
#   ebinternal is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebinternal is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebinternal.  If not, see <http://www.gnu.org/licenses/>.
#

import os

DEBUG = True

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_USER = ''
DATABASE_HOST = ''
DATABASE_NAME = 'internal'

INSTALLED_APPS = (
    'django.contrib.humanize',
    'ebinternal.citypoll',
    'ebinternal.feedback',
)

TEMPLATE_DIRS = (
    os.path.normpath(os.path.join(os.path.dirname(__file__), 'templates')),
)

ROOT_URLCONF = 'ebinternal.urls'

EB_MEDIA_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), 'media'))
EB_MEDIA_URL = ''

# The "from" address of email sent from the feedback application.
EB_FROM_EMAIL = ''

# The email address where notification of new feedback should be sent.
EB_NOTIFICATION_EMAIL = ''

# A mapping from REMOTE_USERs to (name, full_name) tuples. It is assumed that
# the REMOTE_USER will be an email address.
EB_STAFF = {
    '': ('Staff', 'feedback@example.com'),
    # example
    #'john.doe@example.com': ('John', 'John Doe')
}

# This is used in mail signatures as well as for parsing out which page
# feedback came from.
EB_DOMAIN_NAME = 'example.com'
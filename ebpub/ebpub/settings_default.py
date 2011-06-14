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
This file should rarely need editing; if it does, you might want to
move the setting in question into settings.py (and settings.py.in)

Known required settings are: %r
"""

import os
import imp

EBPUB_DIR = imp.find_module('ebpub')[1]
DJANGO_DIR = imp.find_module('django')[1]


########################
# CORE DJANGO SETTINGS #
########################

required_settings=[
    'DEBUG',
]

TEMPLATE_DIRS = (
    os.path.join(EBPUB_DIR, 'templates'),
    os.path.join(DJANGO_DIR, 'contrib', 'gis', 'templates'),
    # django template override hack to partially override templates
    # by referring to them with a unique path, see:
    # http://stackoverflow.com/questions/3967801/django-overriding-and-extending-an-app-template
    # You can use {% extends "ebpub/templates/..." %} to partially extend a template
    os.path.dirname(EBPUB_DIR)
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.Loader'
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'ebpub.accounts.context_processors.user',
    'django.contrib.auth.context_processors.auth',
    'ebpub.db.context_processors.urls',
    'django.core.context_processors.request',
    #'django.core.context_processors.debug',
)

AUTHENTICATION_BACKENDS = (
    'ebpub.accounts.models.AuthBackend',
)

INSTALLED_APPS = (
    'obadmin.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'ebdata.blobs',
    'ebdata.geotagger',
    'ebpub.accounts',
    'ebpub.alerts',
    'ebpub.openblockapi',
    'ebpub.db',
    'ebpub.geocoder',
    'ebpub.petitions',
    'ebpub.preferences',
    'ebpub.savedplaces',
    'ebpub.streets',
    'ebpub.widgets',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django_static',
    # Only need these 2 for some admin tasks, eg. configuration for
    # some scraper-related stuff for the everyblock package.  But I
    # haven't tried to figure out yet which scrapers this might be
    # useful for.
#    'everyblock.admin',
#    'everyblock.staticmedia',
)

APPS_FOR_TESTING = (
    # Don't need these installed at runtime, but I've put them here so
    # manage.py test can automatically find their tests.
    'ebdata.nlp',
    'ebdata.templatemaker',
    'ebdata.textmining',
    'ebpub.metros',
    'ebpub.utils',
    'ebpub.geocoder',
    'ebpub.geocoder.parser',
)

APPS_NOT_FOR_TESTING = (
        # the user model used is custom.
        'django.contrib.auth',
        # this makes too many weird assumptions about the database underpinnings
        'django.contrib.contenttypes',
        # these tests break with some settings, see https://github.com/peterbe/django-static/issues#issue/8 and 9
        'django_static',
        # the rest are just not of interest.
        'django.contrib.sessions',
)


INSTALLED_APPS = INSTALLED_APPS + APPS_FOR_TESTING + ('south',)

TEST_RUNNER = 'obadmin.testrunner.TestSuiteRunner'

# South - database migration config
SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = True

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'ebpub.accounts.middleware.UserMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
)

##################################
# CUSTOM EBPUB & OBDEMO SETTINGS #
##################################


POSTGIS_TEMPLATE = 'template_postgis'

# The domain for your site.
required_settings.append('EB_DOMAIN')

# This is the short name for your city, e.g. "chicago".
required_settings.append('SHORT_NAME')

# Set both of these to distinct, secret strings that include two instances
# of '%s' each. Example: 'j8#%s%s' -- but don't use that, because it's not
# secret.
required_settings.extend(['PASSWORD_CREATE_SALT', 'PASSWORD_RESET_SALT'])

# Database configuration as per
# http://docs.djangoproject.com/en/1.2/topics/db/multi-db/
# There's an example in obdemo/settings.py.in
required_settings.append('DATABASES')

# The list of all metros this installation covers. This is a tuple of
# dictionaries.  If your site only covers one city, there will be
# only one dictionary.
# There's an example in obdemo/settings.py.in
required_settings.append('METRO_LIST')

# Where to center citywide maps by default.
required_settings.append('DEFAULT_MAP_CENTER_LON')
required_settings.append('DEFAULT_MAP_CENTER_LAT')
required_settings.append('DEFAULT_MAP_ZOOM')

# How many days of news to show on many views.
required_settings.append('DEFAULT_DAYS')

EB_MEDIA_ROOT = EBPUB_DIR + '/media'
required_settings.extend(['EB_MEDIA_ROOT'])

# Overrides datetime.datetime.today(), for development.
EB_TODAY_OVERRIDE = None

# This is used as a "From:" in e-mails sent to users.
required_settings.append('GENERIC_EMAIL_SENDER')

# Map stuff.
required_settings.append('MAP_SCALES')
MAP_SCALES = [614400, 307200, 153600, 76800, 38400, 19200, 9600, 4800, 2400, 1200]

# Filesystem location of scraper log.
required_settings.append('SCRAPER_LOGFILE_NAME')

# XXX Unused?
#DATA_HARVESTER_CONFIG = {}

# XXX Unused?
#MAIL_STORAGE_PATH = '/home/mail'

# If this cookie is set with the given value, then the site will give the user
# staff privileges (including the ability to view non-public schemas).
required_settings.extend(['STAFF_COOKIE_NAME', 'STAFF_COOKIE_VALUE'])


# It's important that it be named exactly OpenLayers.js,
# see http://trac.osgeo.org/openlayers/ticket/2982
OPENLAYERS_URL = '/scripts/openlayers-r10972/OpenLayers.js'
#OPENLAYERS_URL = '/scripts/openlayers-2.9.1/OpenLayers.js'
OPENLAYERS_IMG_PATH = '/scripts/openlayers-r10972/img/'

# For local development you might try this:
#JQUERY_URL = '/media/js/jquery.js'
JQUERY_URL = 'http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js'

# Static media optimizations: whitespace slimming, URL timestamping.
# see https://github.com/peterbe/django-static#readme
# This supercedes the everyblock-specific template tags in
# everyblock.templatetags.staticmedia.
DJANGO_STATIC = True
DJANGO_STATIC_MEDIA_ROOTS = [EB_MEDIA_ROOT,
                             EB_MEDIA_ROOT + '/styles',
                             EB_MEDIA_ROOT + '/scripts',
                             ]

# Javascript map options.
# Options for MAP_BASELAYER_TYPE are 'google' or 'wms'.
MAP_BASELAYER_TYPE='wms'
required_settings.append('MAP_BASELAYER_TYPE')

# If you set MAP_BASELAYER_TYPE='wms', you must also set WMS_URL
# and point it to your WMS server.  The default gives you hosted OpenStreetMap tiles.
WMS_URL="http://maps.opengeo.org/geowebcache/service/wms"
# If you set MAP_BASELAYER_TYPE='google', you must also set GOOGLE_MAPS_KEY.
GOOGLE_MAPS_KEY='your API key here'

# Putting django-static's output in a separate directory and URL space
# makes it easier for git to ignore them,
# and easier to have eg. apache set appropriate expiration dates.
DJANGO_STATIC_NAME_PREFIX = '/cache-forever'
DJANGO_STATIC_SAVE_PREFIX = '%s%s' % (EB_MEDIA_ROOT, DJANGO_STATIC_NAME_PREFIX)


# Geocoding.
# Set this True to cache geocoder results in the database;
# it's faster but makes troubleshooting harder.
# (Why doesn't it just use the normal django caching framework?)
EBPUB_CACHE_GEOCODER = True
required_settings.append('EBPUB_CACHE_GEOCODER')

# Logging setup. There's a bit of hackery to make sure we don't set up
# handlers more than once; see
# http://stackoverflow.com/questions/342434/python-logging-in-django


LOGGING_CONFIG=None # TODO: use dictConfig logging config?
# see https://docs.djangoproject.com/en/dev/topics/logging

import logging, threading
_lock = threading.Lock()
with _lock:
    if getattr(logging, '_is_set_up', None) is None:
        logging._is_set_up = True
        if not logging.getLogger().handlers:
            # TODO: configurable file handlers, level...
            # maybe use syslog to avoid contention when running multiple
            # processes under mod_wsgi!
            logging.basicConfig(level=logging.INFO,
                                format="%(asctime)-15s %(levelname)-8s %(message)s")
            # Surprisingly, basicConfig in Python < 2.7 doesn't set
            # the default handler level.  This lets non-root loggers
            # log at ANY level. Fix that.
            for handler in logging.getLogger().handlers:
                handler.setLevel(logging.INFO)
        # need to import this first so it doesn't wipe the level we set...
        from south import logger
        logging.getLogger('south').setLevel(logging.INFO)

__doc__ = __doc__ % required_settings

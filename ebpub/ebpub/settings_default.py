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
    # Database configuration as per
    # http://docs.djangoproject.com/en/1.2/topics/db/multi-db/
    # There's an example in obdemo/settings.py.in
    'DATABASES',
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
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'ebpub.accounts.context_processors.user',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
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
    'django.contrib.messages',
    'ebdata.blobs',
    'ebdata.geotagger',
    'ebpub.accounts',
    'ebpub.alerts',
    'key',
    # openblockapi overrides admin for the 'key' app.
    'ebpub.openblockapi',
    'ebpub.db',
    'ebpub.geocoder',
    'ebpub.petitions',
    'ebpub.preferences',
    'ebpub.richmaps',
    'ebpub.savedplaces',
    'ebpub.streets',
    'ebpub.widgets',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django_static',
    'olwidget',
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

# Messages backend. OpenBlock doesn't use it (yet) but this silences a
# deprecationwarning from the admin UI in django 1.3.
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'


# South - database migration config
SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = True

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'ebpub.accounts.middleware.UserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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
# XXX UNUSED?
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

# For compatibility with django-olwidget
OL_API = OPENLAYERS_URL

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
# TODO: merge this with olwidget config
MAP_BASELAYER_TYPE='wms'
required_settings.append('MAP_BASELAYER_TYPE')

# If you set MAP_BASELAYER_TYPE='wms', you must also set WMS_URL
# and point it to your WMS server.  This default gives you hosted OpenStreetMap tiles.
# TODO: This isn't really functional, we've hardcoded the layer name to 'openstreetmap'
WMS_URL="http://maps.opengeo.org/geowebcache/service/wms"

# If you set MAP_BASELAYER_TYPE='google', you must also set GOOGLE_API_KEY.
GOOGLE_API_KEY='your API key here'

# Which olwidget base layer options to allow switching between?
# See http://olwidget.org/olwidget/v0.4/doc/olwidget.js.html#general-map-display
# for list of possible choices.
# Example:
OLWIDGET_LAYERS = ['google.streets', 'osm.mapnik', 'osm.osmarender', 'cloudmade.36041']


# Hackery to add custom base layers & other js data for customized django-olwidget.
# Currently only applies to admin UI maps.
EXTRA_OLWIDGET_CONTEXT = {
    # Override this to set the default base layer.  eg:
    #'default_base_layer': 'google.streets',
    'default_base_layer': 'OpenStreetMap (OpenGeo)',

    # Custom layers.
    'custom_base_layers':
        [{"class": "WMS",
          "name": "OpenStreetMap (OpenGeo)",
          "url": WMS_URL,
          "params": {"layers": "openstreetmap",
                     "format": "image/png",
                     "bgcolor": "#A1BDC4"
                     },
          "options": {"wrapDateLine": True}
          }
         ]
    }


# Putting django-static's output in a separate directory and URL space
# makes it easier for git to ignore them,
# and easier to have eg. apache set appropriate expiration dates.
DJANGO_STATIC_NAME_PREFIX = '/cache-forever'
DJANGO_STATIC_SAVE_PREFIX = '%s%s' % (EB_MEDIA_ROOT, DJANGO_STATIC_NAME_PREFIX)

# Django 1.3's staticfiles app ... we use django-static instead,
# but olwidget needs this set:
STATIC_URL='/'

# Geocoding.
# Set this True to cache geocoder results in the database;
# it's faster but makes troubleshooting harder.
# (Why doesn't it just use the normal django caching framework?)
EBPUB_CACHE_GEOCODER = True
required_settings.append('EBPUB_CACHE_GEOCODER')

######################################################################
# API Keys for OpenBlock's REST API.
# Warning, if you increase API_KEY_SIZE after running syncdb, you'll
# have to modify the size of the 'key' field in the 'key_apikey' table
# in your database.
API_KEY_SIZE=32
MAX_KEYS_PER_USER=3

API_THROTTLE_AT=150  # max requests per timeframe.
API_THROTTLE_TIMEFRAME = 60 * 60 # default 1 hour.
# How long to retain the times the user has accessed the API. Default 1 week.
API_THROTTLE_EXPIRATION = 60 * 60 * 24 * 7

# NOTE in order to enable throttling, you MUST also configure
# CACHES['default'] to something other than a DummyCache.  See CACHES
# below.

#########################################################################
## For development & testing, DummyCache makes for easiest troubleshooting.
## See https://docs.djangoproject.com/en/1.3/ref/settings/#std:setting-CACHES
#
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    # File caching might be a reasonable choice for low-budget, memory-constrained
    # hosting environments.
    # 'default': {
    #     'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
    #     'LOCATION': 'file:///tmp/myblock_cache',
    # }
}



# Required by django-apikey to associate keys with user profiles.
AUTH_PROFILE_MODULE = 'preferences.Profile'

###################################################################
# Logging.
# See https://docs.djangoproject.com/en/dev/topics/logging
# We import this first because South annoyingly overrides its log level at import time.
from south import logger as _unused

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
        'simple': {
            'format': '%(levelname)s %(module)s: %(message)s'
            },
        'debug': {'format': '%(levelname)s %(asctime)s P: (process)d T: %(thread)d in %(module)s:%(pathname)s:%(lineno)d %(message)s'
                  },
        'verbose': {'format': '%(levelname)s %(asctime)s P: (process)d T: %(thread)d in %(module)s: % %(message)s'
                    },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
            },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
            },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose'
            },
        },
    'loggers': {
        '': {
            'handlers':['console'],
            'propagate': True,
            'level':'INFO',
            },
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
            },
        'ebpub': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
            },
        'ebdata': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
            },
        # django.request logs all 404s at level WARN; not very useful
        # and annoying during tests.
        'django.request': {
            'handlers':['console'],
            'propagate': True,
            'level':'ERROR',
        },
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        'south': {
            'handlers': ['console',],
            'level': 'INFO',
        }
    }
}

__doc__ = __doc__ % required_settings

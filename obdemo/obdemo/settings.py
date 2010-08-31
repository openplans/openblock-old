"""
All deployment-specific config should be put in a module named
'real_settings.py'

This file should rarely need editing; if it does, you might want to
move the setting in question into real_settings.py

Known required settings are: %r
"""

import os
import imp


########################
# CORE DJANGO SETTINGS #
########################

DATABASE_ENGINE = 'postgresql_psycopg2' # ebpub only supports postgresql_psycopg2.

_required_settings=[
    'DATABASE_NAME', 'DATABASE_USER', 'DATABASE_PASSWORD',
    'DATABASE_HOST', 'DATABASE_PORT', 'DATABASE_ENGINE',
    'DEBUG',
]    

POSTGIS_TEMPLATE = 'template_postgis'

EBPUB_DIR = imp.find_module('ebpub')[1]
EB_DIR = imp.find_module('everyblock')[1]

TEMPLATE_DIRS = (
    os.path.normpath(os.path.join(os.path.dirname(__file__), 'templates')),
    EBPUB_DIR + '/templates',
    EB_DIR + '/templates',
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'ebpub.accounts.context_processors.user',
    #'django.core.context_processors.debug',
)


INSTALLED_APPS = (
    'ebdata.blobs',
    'ebpub.accounts',
    'ebpub.alerts',
    'ebpub.db',
    'ebpub.geocoder',
    'ebpub.petitions',
    'ebpub.preferences',
    'ebpub.savedplaces',
    'ebpub.streets',
    'django.contrib.humanize',
    'django.contrib.sessions',

    # Don't need these installed at runtime, but I've put them here so
    # manage.py test can automatically find their tests.
    'ebdata.nlp',
    'ebdata.templatemaker',
    'ebdata.textmining',
    'ebgeo.maps',
    'ebgeo.utils',

    # Only need these 2 for some admin tasks, eg. configuration for
    # some scraper-related stuff for the everyblock package.  But I
    # haven't tried to figure out yet which scrapers this might be
    # useful for.
    'everyblock.admin',
    'everyblock.staticmedia',

)
TEST_RUNNER='django.contrib.gis.tests.run_tests'

ROOT_URLCONF = 'obdemo.urls'
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'ebpub.accounts.middleware.UserMiddleware',
)

#########################
# CUSTOM EBPUB SETTINGS #
#########################

# We've moved many settings to another (not-version-controlled) file.
# You'll get alerted by an error if anything required is not in that file.
# We import those settings twice: once up here to allow other settings
# to derive from them, and once at the end to override any defaults.
from real_settings import *

# The domain for your site.
_required_settings.append('EB_DOMAIN')

# This is the short name for your city, e.g. "chicago".
_required_settings.append('SHORT_NAME')

# Set both of these to distinct, secret strings that include two instances
# of '%s' each. Example: 'j8#%s%s' -- but don't use that, because it's not
# secret.
_required_settings.extend(['PASSWORD_CREATE_SALT', 'PASSWORD_RESET_SALT'])

# Here, we define the different databases we use, giving each one a label
# (like 'users') so we can refer to a particular database via multidb
# managers.
#
# Note that we only need to define databases that are used by multidb
# managers -- not our default database for this settings file. Any Django
# model code that doesn't use the multidb manager will use the standard
# DATABASE_NAME/DATABASE_USER/etc. settings.
#
# THE UPSHOT: If you're only using one database, the only thing you'll need
# to set here is TIME_ZONE.
_required_settings.append('DATABASES')

DATABASES = {
    'users': {
        'DATABASE_HOST': DATABASE_HOST,
        'DATABASE_NAME': DATABASE_NAME,
        'DATABASE_OPTIONS': {},
        'DATABASE_PASSWORD': '',
        'DATABASE_PORT': DATABASE_PORT,
        'DATABASE_USER': DATABASE_USER,
        'TIME_ZONE': '', # Same format as Django's TIME_ZONE setting.
    },
    'metros': {
        'DATABASE_HOST': DATABASE_HOST,
        'DATABASE_NAME': DATABASE_NAME,
        'DATABASE_OPTIONS': {},
        'DATABASE_PASSWORD': '',
        'DATABASE_PORT': DATABASE_PORT,
        'DATABASE_USER': DATABASE_USER, 
        'TIME_ZONE': '', # Same format as Django's TIME_ZONE setting.
    },
}

# The list of all metros this installation covers. This is a tuple of
# dictionaries.
_required_settings.append('METRO_LIST')
METRO_LIST = (
    # Example dictionary:
    {
    #     # Extent of the metro, as a longitude/latitude bounding box.
        'extent': (-71.191153, 42.227865, -70.986487, 42.396978),
    #
    #     # Whether this should be displayed to the public.
        'is_public': True,
    #
    #     # Set this to True if the metro has multiple cities.
        'multiple_cities': False,
    #
    #     # The major city in the metro.
        'city_name': 'Boston',
    #
    #     # The SHORT_NAME in the settings file (also the subdomain).
        'short_name': 'boston',
    #
    #     # The name of the metro, as opposed to the city (e.g., "Miami-Dade" instead of "Miami").
        'metro_name': 'Boston',
    #
    #     # USPS abbreviation for the state.
        'state': 'MA',
    #
    #     # Full name of state.
        'state_name': 'Massachusetts',
    #
    #     # Time zone, as required by Django's TIME_ZONE setting.
        'time_zone': 'America/New_York',
    },
)

import os
OBDEMO_DIR = os.path.normpath(os.path.dirname(__file__))
EB_MEDIA_ROOT = OBDEMO_DIR + '/media' # necessary for static media versioning
EB_MEDIA_URL = '' # leave at '' for development
_required_settings.extend(['EB_MEDIA_URL', 'EB_MEDIA_ROOT'])

# Overrides datetime.datetime.today(), for development.
EB_TODAY_OVERRIDE = None

# Filesystem location of shapefiles for maps, e.g., '/home/shapefiles'.
# Used only by ebgeo/maps/tess.py
SHAPEFILE_ROOT = ''
_required_settings.append('SHAPEFILE_ROOT')

# For the 'autoversion' template tag.
_required_settings.append('AUTOVERSION_STATIC_MEDIA')
AUTOVERSION_STATIC_MEDIA = False


# Connection info for mapserver.
# Leave these alone if you're not using one;
# by default obdemo doesn't need it.
MAPS_POSTGIS_HOST = '127.0.0.1'
MAPS_POSTGIS_USER = ''
MAPS_POSTGIS_PASS = ''
MAPS_POSTGIS_DB = ''

_required_settings.extend([
        'MAPS_POSTGIS_HOST', 'MAPS_POSTGIS_USER', 'MAPS_POSTGIS_PASS',
        'MAPS_POSTGIS_DB',
])


# This is used as a "From:" in e-mails sent to users.
_required_settings.append('GENERIC_EMAIL_SENDER')

# Map stuff.
_required_settings.extend(['MAP_SCALES', 'SPATIAL_REF_SYS', 'MAP_UNITS'])
MAP_SCALES = [614400, 307200, 153600, 76800, 38400, 19200, 9600, 4800, 2400, 1200]
SPATIAL_REF_SYS = '900913' # Spherical Mercator
MAP_UNITS = 'm' # see ebgeo.maps.utils for allowed unit types

# Filesystem location of tilecache config (e.g., '/etc/tilecache/tilecache.cfg').
# obdemo doesn't use a tilecache out of the box.
TILECACHE_CONFIG = '/etc/tilecache.cfg'
TILECACHE_ZOOM = 17
TILECACHE_LAYER = 'osm'
TILECACHE_VERSION = '1.0.0'
TILECACHE_EXTENSION = 'png'

# Filesystem location of scraper log.
_required_settings.append('SCRAPER_LOGFILE_NAME')

# XXX Unused?
#DATA_HARVESTER_CONFIG = {}

# XXX Unused?
#MAIL_STORAGE_PATH = '/home/mail'

# If this cookie is set with the given value, then the site will give the user
# staff privileges (including the ability to view non-public schemas).
_required_settings.extend(['STAFF_COOKIE_NAME', 'STAFF_COOKIE_VALUE'])


# Re-import from real_settings to override any defaults in this file.
from real_settings import *

for name in _required_settings:
    if not name in globals():
        raise NameError("Required setting %r was not defined in real_settings.py or settings.py" % name)

__doc__ = __doc__ % _required_settings

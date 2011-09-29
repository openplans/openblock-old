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
obdemo-specific stuff we might need in templates.
"""

from django.conf import settings
from django.utils import simplejson
from ebpub.db.utils import today

def _get_map_media():
    from olwidget.widgets import Map
    layers = [settings.MAP_BASELAYER_TYPE]
    map_media = Map([], options={'layers': layers}).media
    return map_media.render()

def _get_extra_layers():
    layers = getattr(settings, 'MAP_CUSTOM_BASE_LAYERS', [])
    return simplejson.dumps(layers, indent=2)

def map_context(request):
    """
    Context variables needed on pages that use maps.
    """
    # XXX TODO: can we slim or at least version the olwidget JS & CSS?
    # note they are set as settings.OLWIDGET_JS and settings.OLWIDGET_CSS,
    # could possibly munge those?
    return {'OPENLAYERS_IMG_PATH': settings.OPENLAYERS_IMG_PATH,
            'JQUERY_URL': settings.JQUERY_URL,
            'MAP_MEDIA_HTML': _get_map_media,
            'MAP_CUSTOM_BASE_LAYERS': _get_extra_layers,
            'MAP_BASELAYER_TYPE': settings.MAP_BASELAYER_TYPE,
            'alerts_installed': 'ebpub.alerts' in settings.INSTALLED_APPS,
            'today': today(),
            }

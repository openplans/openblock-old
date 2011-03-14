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

def urls(request):
    return {'OPENLAYERS_URL': settings.OPENLAYERS_URL,
            'OPENLAYERS_IMG_PATH': settings.OPENLAYERS_IMG_PATH,
            'MAP_BASELAYER_TYPE': settings.MAP_BASELAYER_TYPE,
            'GOOGLE_MAPS_KEY': getattr(settings, 'GOOGLE_MAPS_KEY', '') or '',
            'WMS_URL': getattr(settings, 'WMS_URL', '') or '',
            }

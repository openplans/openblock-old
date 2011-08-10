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
Admin UI classes and Widgets with maps customized for OpenBlock,
based on django-olwidget.
"""

from copy import deepcopy
from django.conf import settings
from django.utils import simplejson
from olwidget.admin import GeoModelAdmin
from olwidget.fields import MapField, EditableLayerField
from olwidget.widgets import Map
import logging

logger = logging.getLogger('ebpub.geoadmin')

# Base options for olwidget, used by maps in the admin UI.
# TODO: olwidget already checks for OLWIDGET_DEFAULT_OPTIONS in settings,
# so this should move to default_settings; but it depends on other
# settings that are probably user-defined.

OLWIDGET_DEFAULT_OPTIONS = getattr(settings, 'OLWIDGET_DEFAULT_OPTIONS', None) or \
    {
    'default_lat': settings.DEFAULT_MAP_CENTER_LAT,
    'default_lon': settings.DEFAULT_MAP_CENTER_LON,
    'default_zoom': settings.DEFAULT_MAP_ZOOM,
    'zoom_to_data_extent': True,
    'layers': [settings.MAP_BASELAYER_TYPE],
    'controls': ['Navigation', 'PanZoom', 'Attribution'],
    # Defaults for generic GeometryFields.
    'geometry': ['point', 'linestring', 'polygon'],
    'isCollection': True,
    # These are necessary to keep our default OSM WMS layer happy.
    'map_options': {'max_resolution': 156543.03390625,
                    'num_zoom_levels': 19,
                    },
    }


class OBMapWidget(Map):

    @classmethod
    def get_extra_context(klass):
        """
        Hook provided by our hacked version of django-olwidget.
        Stuffs a dict of JSON-encoded values into the template
        context so we can provide extra data to our customized
        map template.
        """
        from ebpub.db.context_processors import _get_extra_layers
        return {'MAP_CUSTOM_BASE_LAYERS': _get_extra_layers}

# Need this for changelist maps and other places that aren't convenient to
# override via subclassing.
Map.get_extra_context = OBMapWidget.get_extra_context

class OBMapField(MapField):
    """
    A FormField just like olwidget's MapField but the default widget
    is OBMapWidget, with our default options.
    """

    def __init__(self, fields=None, options=None, layer_names=None,
                 template=None, **kwargs):
        merged_options = deepcopy(OLWIDGET_DEFAULT_OPTIONS)
        if options:
            merged_options.update(options)
        if not fields:
            fields = [EditableLayerField(required=kwargs.get('required'))]
        layers = [field.widget for field in fields]
        self.fields = fields
        kwargs['widget'] = kwargs.get(
            'widget',
            OBMapWidget(layers, merged_options, template, layer_names))
        super(OBMapField, self).__init__(fields=fields, options=merged_options,
                                         layer_names=layer_names,
                                         template=template, **kwargs)


class OSMModelAdmin(GeoModelAdmin):

    options = deepcopy(OLWIDGET_DEFAULT_OPTIONS)

    # This relies on a hack in our forked version of olwidget.
    default_field_class = OBMapField

    list_map_options = deepcopy(options)
    list_map_options['zoom_to_data_extent'] = False

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context.update(OBMapWidget.get_extra_context())
        return super(OSMModelAdmin, self).changelist_view(request, extra_context)

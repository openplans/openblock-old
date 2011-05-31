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
from django.contrib.gis.forms import GeometryField
from django.template.loader import render_to_string
from django.utils import simplejson
from ebpub.utils.geodjango import flatten_geomcollection
from olwidget import utils
from olwidget.admin import GeoModelAdmin
from olwidget.fields import MapField, EditableLayerField
from olwidget.widgets import Map


import logging

logger = logging.getLogger('ebpub.geoadmin')

# Base options for olwidget, used by maps in the admin UI.
# TODO: olwidget already checks for OLWIDGET_DEFAULT_OPTIONS in settings,
# so this should move to default_settings; but it depends on other
# settings are probably user-defined.
OLWIDGET_DEFAULT_OPTIONS = getattr(settings, 'OLWIDGET_DEFAULT_OPTIONS', None) or \
    {
    'default_lat': settings.DEFAULT_MAP_CENTER_LAT,
    'default_lon': settings.DEFAULT_MAP_CENTER_LON,
    'default_zoom': settings.DEFAULT_MAP_ZOOM,
    'zoom_to_data_extent': True,
    'layers': ['google.streets', 'osm.mapnik', 'osm.osmarender',
               'cloudmade.36041'],
    # TODO: We don't really want LayerSwitcher on all maps, just
    # on one map that saves the chosen layer in some config somewhere.
    'controls': ['LayerSwitcher', 'Navigation', 'PanZoom', 'Attribution'],

    # Defaults for generic GeometryFields.
    'geometry': ['point', 'linestring', 'polygon'],
    'isCollection': True,
    # These are necessary to keep our default OSM WMS layer happy.
    'map_options': {'max_resolution': 156543.03390625,
                    'num_zoom_levels': 19,
                    },
    }


class OBMapWidget(Map):
    def render(self, name, value, attrs=None):
        """Same as olwidget.widgets.Map.render(),
        except with one extra line to insert a tiny bit of extra
        context for the template from settings.py.
        """
        if value is None:
            values = [None for i in range(len(self.vector_layers))]
        elif not isinstance(value, (list, tuple)):
            values = [value]
        else:
            values = value
        attrs = attrs or {}
        # Get an arbitrary unique ID if we weren't handed one (e.g. widget used
        # outside of a form).
        map_id = attrs.get('id', "id_%s" % id(self))

        layer_js = []
        layer_html = []
        layer_names = self._get_layer_names(name)
        value_count = 0
        for i, layer in enumerate(self.vector_layers):
            if layer.editable:
                value = values[value_count]
                value_count += 1
            else:
                value = None
            lyr_name = layer_names[i]
            id_ = "%s_%s" % (map_id, lyr_name)
            # Use "prepare" rather than "render" to get both js and html
            (js, html) = layer.prepare(lyr_name, value, attrs={'id': id_ })
            layer_js.append(js)
            layer_html.append(html)

        attrs = attrs or {}

        context = {
            'id': map_id,
            'layer_js': layer_js,
            'layer_html': layer_html,
            'map_opts': simplejson.dumps(utils.translate_options(self.options)),
        }
        ##### OpenBlock customizations start here ############
        context.update(_get_olwidget_extra_context())
        ##### End of OpenBlock customizations ############
        return render_to_string(self.template, context)


def _get_olwidget_extra_context():
    raw = getattr(settings, 'EXTRA_OLWIDGET_CONTEXT', {})
    context = {}
    for key, val in raw.items():
        context[key] = simplejson.dumps(val)
    return context

class OBMapField(MapField, GeometryField):
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

    def clean(self, value):
        """
        Return an array with the value from each layer.
        """
        # This is rather awkward: MapField expects to get / return a
        # list, but it doesn't convert strings to geometry objects (it
        # doesn't inherit from GeometryField, I don't know why).

        # Meanwhile, GeometryField.clean() does do string -> geometry
        # conversion, but *it* expects to get a single string value.
        # So, we explicitly call both.

        # There's some metaclass voodoo in GeoModelAdmin that patches
        # up existing GeometryField instances with clobbered widgets
        # so everything works, but that only happens if the existing
        # widgets aren't already MapFields ... which ours are.
        locations = MapField.clean(self, value)
        if not isinstance(locations, list):
            locations = [locations]
        locations = [GeometryField.clean(self, loc) for loc in locations]
        # Fix GeometryCollections, bug #95.
        locations = [flatten_geomcollection(loc) if loc else None
                     for loc in locations]
        return locations


class OSMModelAdmin(GeoModelAdmin):

    options = deepcopy(OLWIDGET_DEFAULT_OPTIONS)

    # This relies on a hack in our forked version of olwidget.
    default_field_class = OBMapField

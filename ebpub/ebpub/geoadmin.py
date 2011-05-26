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
Admin UI classes and Widgets with maps customized for OpenBlock.
"""

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import simplejson
from olwidget import utils
from olwidget.admin import GeoModelAdmin
from olwidget.widgets import Map


"""
See http://docs.djangoproject.com/en/dev/ref/contrib/gis/admin/
"""


class OSMModelAdmin(GeoModelAdmin):
    options = {
        'default_lat': settings.DEFAULT_MAP_CENTER_LAT,
        'default_lon': settings.DEFAULT_MAP_CENTER_LON,
        'default_zoom': settings.DEFAULT_MAP_ZOOM,
        'zoom_to_data_extent': True,
        'layers': ['google.streets', 'osm.mapnik', 'osm.osmarender'],
        'controls': ['LayerSwitcher', 'Navigation', 'PanZoom', 'Attribution'],

        # These are necessary to keep our default OSM WMS layer happy.
        'map_options': {'max_resolution': 156543.03390625,
                        'num_zoom_levels': 19},
        }

    def get_form(self, *args, **kwargs):
        """
        Override GeoModelAdmin.get_form(), which sets up the olwidget
        map widgets, to use our own tweaked widget.

        Unfortunately, given that these fields have their widgets
        replaced somewhat sneakily by olwidget, there's not a better
        hook that I see for getting a custom Widget class in there.
        """
        form = GeoModelAdmin.get_form(self, *args, **kwargs)
        fields = form.base_fields
        for key, field in fields.items():
            if isinstance(field.widget, Map):
                print "SWAPPING IT: %r" % key
                field.widget = OBMapWidget(vector_layers=field.widget.vector_layers,
                                           options=field.widget.options,
                                           template=field.widget.template,
                                           layer_names=field.widget.layer_names
                                           )

        return form


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
        context.update(getattr(settings, 'EXTRA_OLWIDGET_CONTEXT', {}))
        ##### End of OpenBlock customizations ############
        return render_to_string(self.template, context)


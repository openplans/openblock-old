from django.conf import settings
from django.contrib.gis import admin
from django.contrib.gis.admin.widgets import OpenLayersWidget
from django.contrib.gis.admin.widgets import geo_context
from django.contrib.gis.gdal import OGRException
from django.contrib.gis.gdal import OGRGeomType
from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.template import loader
from ebpub.db.models import Attribute
from ebpub.db.models import Location
from ebpub.db.models import LocationType
from ebpub.db.models import NewsItem
from ebpub.db.models import Schema
from ebpub.db.models import SchemaField


"""
See http://docs.djangoproject.com/en/dev/ref/contrib/gis/admin/
"""

class OBOpenLayersWidget(OpenLayersWidget):
    """
    Renders an OpenLayers map using the WKT of the geometry.

    OVERRIDING FOR OPENBLOCK: This subclass has patched methods as per
    http://code.djangoproject.com/attachment/ticket/9806/9806.3.diff
    and we can delete it if/when
    http://code.djangoproject.com/ticket/9806 gets fixed.
    """
    def render(self, name, value, attrs=None):
        # Update the template parameters with any attributes passed in.
        if attrs: self.params.update(attrs)

        # Defaulting the WKT value to a blank string -- this
        # will be tested in the JavaScript and the appropriate
        # interface will be constructed.
        self.params['wkt'] = ''

        # If a string reaches here (via a validation error on another
        # field) then just reconstruct the Geometry.
        if isinstance(value, basestring):
            try:
                value = GEOSGeometry(value)
            except (GEOSException, ValueError):
                value = None
        if value and value.geom_type.upper() != self.geom_type and self.geom_type != 'GEOMETRY':
            value = None

        # Constructing the dictionary of the map options.
        self.params['map_options'] = self.map_options()

        # Constructing the JavaScript module name using the name of
        # the GeometryField (passed in via the `attrs` keyword).
        # Use the 'name' attr for the field name (rather than 'field')
        self.params['name'] = name
        # note: we must switch out dashes for underscores since js
        # functions are created using the module variable
        js_safe_name = self.params['name'].replace('-','_')
        self.params['module'] = 'geodjango_%s' % js_safe_name

        if value:
            # Transforming the geometry to the projection used on the
            # OpenLayers map.
            srid = self.params['srid']
            if value.srid != srid:
                try:
                    ogr = value.ogr
                    ogr.transform(srid)
                    wkt = ogr.wkt
                except OGRException:
                    wkt = ''
            else:
                wkt = value.wkt

            # Setting the parameter WKT with that of the transformed
            # geometry.
            self.params['wkt'] = wkt

            # Check if the field is generic so the proper values are overriden
            if self.params['is_unknown']:
                self.params['geom_type'] = OGRGeomType(value.geom_type)
                if value.geom_type.upper() in ('LINESTRING', 'MULTILINESTRING'):
                    self.params['is_linestring'] = True
                elif value.geom_type.upper() in ('POLYGON', 'MULTIPOLYGON'):
                    self.params['is_polygon'] = True
                elif value.geom_type.upper() in ('POINT', 'MULTIPOINT'):
                    self.params['is_point'] = True
                if value.geom_type.upper() in ('MULTIPOINT', 'MULTILINESTRING', 'MULTIPOLYGON', 'GEOMETRYCOLLECTION'):
                    self.params['is_collection']=True
                    if value.geom_type.upper() == 'GEOMETRYCOLLECTION':
                        self.params['collection_type'] = 'Any'
                    else:
                        self.params['collection_type'] = OGRGeomType(value.geom_type.upper().replace('MULTI', ''))

        else:
            if self.params['is_unknown']:
                # If the geometry is unknown and the value is not set, make it as flexible as possible.
                self.params['geom_type'] = OGRGeomType('GEOMETRYCOLLECTION')
                self.params['is_collection']=True
                self.params['collection_type'] = 'Any'

        return loader.render_to_string(self.template, self.params,
                                       context_instance=geo_context)


class OSMModelAdmin(admin.GeoModelAdmin):
    # Use GeoModelAdmin to get editable geometries.
    # But we'll override a few defaults to use an OpenStreetMap base layer.
    default_zoom = 11
    openlayers_url = getattr(settings, 'OPENLAYERS_URL', admin.GeoModelAdmin.openlayers_url)
    point_zoom = 14
    wms_layer = 'openstreetmap'
    wms_name = 'OpenStreetMap'
    wms_url = 'http://maps.opengeo.org/geowebcache/service/wms'
    widget = OBOpenLayersWidget
    wms_options = {'format': 'image/png'}

    # Upstream patch for geodjango submitted:
    # http://code.djangoproject.com/ticket/14886 ... to allow passing
    # parameters to the WMS layer constructor.  If/when that's fixed,
    # we could remove our copy of openlayers.js.

    @property
    def default_lat(self):
        return settings.DEFAULT_MAP_CENTER_LAT

    @property
    def default_lon(self):
        return settings.DEFAULT_MAP_CENTER_LON

    def get_map_widget(self, db_field):
        """
        Returns a subclass of the OpenLayersWidget (or whatever was specified
        in the `widget` attribute) using the settings from the attributes set
        in this class.

        OVERRIDING FOR OPENBLOCK: This is the patched version of this
        method as per
        http://code.djangoproject.com/attachment/ticket/9806/9806.3.diff
        and we can delete it if/when
        http://code.djangoproject.com/ticket/9806 gets fixed.
        """
        is_unknown = db_field.geom_type in ('GEOMETRY',)
        if not is_unknown:
            #If it is not generic, get the parameters from the db_field
            is_collection = db_field.geom_type in ('MULTIPOINT', 'MULTILINESTRING', 'MULTIPOLYGON', 'GEOMETRYCOLLECTION')
            if is_collection:
                if db_field.geom_type == 'GEOMETRYCOLLECTION': collection_type = 'Any'
                else: collection_type = OGRGeomType(db_field.geom_type.upper().replace('MULTI', ''))
            else:
                collection_type = 'None'
            is_linestring = db_field.geom_type in ('LINESTRING', 'MULTILINESTRING')
            is_polygon = db_field.geom_type in ('POLYGON', 'MULTIPOLYGON')
            is_point = db_field.geom_type in ('POINT', 'MULTIPOINT')
            geom_type = OGRGeomType(db_field.geom_type)
        else:
            #If it is generic, set sensible defaults
            is_collection = False
            collection_type = 'None'
            is_linestring = False
            is_polygon = False
            is_point = False
            geom_type = OGRGeomType('Unknown')

        class OLMap(self.widget):
            template = self.map_template
            geom_type = db_field.geom_type
            wms_options = ''
            if self.wms_options:
                wms_options = ["%s: '%s'" % pair for pair in self.wms_options.items()]
                wms_options = ', '.join(wms_options)
                wms_options = ', ' + wms_options

            params = {'default_lon' : self.default_lon,
                      'default_lat' : self.default_lat,
                      'default_zoom' : self.default_zoom,
                      'display_wkt' : self.debug or self.display_wkt,
                      'geom_type' : geom_type,
                      'field_name' : db_field.name,
                      'is_unknown': is_unknown,
                      'is_collection' : is_collection,
                      'scrollable' : self.scrollable,
                      'layerswitcher' : self.layerswitcher,
                      'collection_type' : collection_type,
                      'is_linestring' : is_linestring,
                      'is_polygon' : is_polygon,
                      'is_point' : is_point,
                      'num_zoom' : self.num_zoom,
                      'max_zoom' : self.max_zoom,
                      'min_zoom' : self.min_zoom,
                      'units' : self.units, #likely shoud get from object
                      'max_resolution' : self.max_resolution,
                      'max_extent' : self.max_extent,
                      'modifiable' : self.modifiable,
                      'mouse_position' : self.mouse_position,
                      'scale_text' : self.scale_text,
                      'map_width' : self.map_width,
                      'map_height' : self.map_height,
                      'point_zoom' : self.point_zoom,
                      'srid' : self.map_srid,
                      'display_srid' : self.display_srid,
                      'wms_url' : self.wms_url,
                      'wms_layer' : self.wms_layer,
                      'wms_name' : self.wms_name,
                      'wms_options': wms_options,
                      'debug' : self.debug,
                      }
        return OLMap

class AttributeInline(admin.StackedInline):
    # TODO: this badly needs a custom Form that takes into account the
    # Schema and shows you only relevant fields, with labels.
    model = Attribute

class NewsItemAdmin(OSMModelAdmin):
    inlines = [
        AttributeInline,
        ]

    list_display = ('title', 'schema', 'item_date', 'pub_date', 'location_name')
    list_filter = ('schema',)

class LocationAdmin(OSMModelAdmin):
    pass


admin.site.register(Schema)
admin.site.register(SchemaField)
#admin.site.register(Attribute, AttributeAdmin)
admin.site.register(NewsItem, NewsItemAdmin)
admin.site.register(LocationType)
admin.site.register(Location, LocationAdmin)


// Overrides for Openblock: support multipolygon and multipoint.
// Upstream patch submitted to http://code.djangoproject.com/ticket/9806
{# Author: Justin Bronn, Travis Pinney & Dane Springmeyer #}
{% block vars %}var {{ module }} = {};
{% if openlayers_img_path %}OpenLayers.ImgPath = '{{ openlayers_img_path }}';{% endif %}
{{ module }}.map = null; {{ module }}.controls = null; {{ module }}.panel = null; {{ module }}.re = new RegExp("^SRID=\d+;(.+)", "i"); {{ module }}.layers = {};
{{ module }}.modifiable = {{ modifiable|yesno:"true,false" }};
{{ module }}.wkt_f = new OpenLayers.Format.WKT();
{{ module }}.is_collection = {{ is_collection|yesno:"true,false" }};
{{ module }}.collection_type = '{{ collection_type }}';
{{ module }}.is_linestring = {{ is_linestring|yesno:"true,false" }};
{{ module }}.is_polygon = {{ is_polygon|yesno:"true,false" }};
{{ module }}.is_point = {{ is_point|yesno:"true,false" }};
{% endblock %}
{{ module }}.get_ewkt = function(feat){
  return 'SRID={{ srid }};' + {{ module }}.wkt_f.write(feat);
};
{{ module }}.read_wkt = function(wkt){
  // OpenLayers cannot handle EWKT -- we make sure to strip it out.
  // EWKT is only exposed to OL if there's a validation error in the admin.
  var match = {{ module }}.re.exec(wkt);
  if (match){wkt = match[1];}
  return {{ module }}.wkt_f.read(wkt);
};
{{ module }}.write_wkt = function(feat){
  if (({{ module }}.is_collection) && (feat.geometry.components != undefined) ){
    {{ module }}.num_geom = feat.geometry.components.length;
  } else {
    {{ module }}.num_geom = 1;
  };
  // XXX FIXME when saving a feature that's a GeometryCollection,
  // either on edit or on initial creation,
  // this sets the wkt blank with no points, like GEOMETRY( ),
  // which gives a GEOS validation error from the python side.
  // see openlayers bug http://trac.osgeo.org/openlayers/ticket/2240
  document.getElementById('{{ id }}').value = {{ module }}.get_ewkt(feat);
};
{{ module }}.add_wkt = function(event){
  // This function will sync the contents of the `vector` layer with the
  // WKT in the text field.
  if ({{ module }}.is_collection){
    var feat = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.{{ geom_type }}());
    for (var i = 0; i < {{ module }}.layers.vector.features.length; i++){
      feat.geometry.addComponents({{ module }}.layers.vector.features[i].geometry.components);
    }
    {{ module }}.write_wkt(feat);
  } else {
    // Make sure to remove any previously added features.
    if ({{ module }}.layers.vector.features.length > 1){
      old_feats = [{{ module }}.layers.vector.features[0]];
      {{ module }}.layers.vector.removeFeatures(old_feats);
      {{ module }}.layers.vector.destroyFeatures(old_feats);
    }
    {{ module }}.write_wkt(event.feature);
  }
};
{{ module }}.modify_wkt = function(event){
  if ({{ module }}.is_collection){
    if ({{ module }}.is_point){
      {{ module }}.add_wkt(event);
      return;
    } else {
      // When modifying the selected components are added to the
      // vector layer so we only increment to the `num_geom` value.
      var feat = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.{{ geom_type }}());
      for (var i = 0; i < {{ module }}.num_geom; i++){
	feat.geometry.addComponents({{ module }}.layers.vector.features[i].geometry.components);
      }
      {{ module }}.write_wkt(feat);
    }
  } else {
    {{ module }}.write_wkt(event.feature);
  }
};
// Function to clear vector features and purge wkt from div
{{ module }}.deleteFeatures = function(){
  {{ module }}.layers.vector.removeFeatures({{ module }}.layers.vector.features);
  {{ module }}.layers.vector.destroyFeatures();
}
{{ module }}.clearFeatures = function (){
  {{ module }}.deleteFeatures();
  document.getElementById('{{ id }}').value = '';
  {{ module }}.map.setCenter(new OpenLayers.LonLat({{ default_lon }}, {{ default_lat }}), {{ default_zoom }});
};
// Add Select control
{{ module }}.addSelectControl = function(){
  var select = new OpenLayers.Control.SelectFeature({{ module }}.layers.vector, {'toggle' : true, 'clickout' : true});
  {{ module }}.map.addControl(select);
  select.activate();
};
{{ module }}.enableDrawing = function(){ {{ module }}.map.getControlsByClass('OpenLayers.Control.DrawFeature')[0].activate();};
{{ module }}.enableEditing = function(){ {{ module }}.map.getControlsByClass('OpenLayers.Control.ModifyFeature')[0].activate();};
// Create an array of controls based on geometry type
{{ module }}.getControls = function(lyr){
  {{ module }}.panel = new OpenLayers.Control.Panel({'displayClass': 'olControlEditingToolbar'});
  var nav = new OpenLayers.Control.Navigation({'title': 'Navigate'});
  var draw_ctl;
  if ({{ module }}.is_linestring){
    draw_ctl = new OpenLayers.Control.DrawFeature(lyr, OpenLayers.Handler.Path, {'displayClass': 'olControlDrawFeaturePath', 'title': 'Draw Lines'});
  } else if ({{ module }}.is_polygon){
    draw_ctl = new OpenLayers.Control.DrawFeature(lyr, OpenLayers.Handler.Polygon, {'displayClass': 'olControlDrawFeaturePolygon', 'title': 'Draw Polygons'});
  } else if ({{ module }}.is_point){
    draw_ctl = new OpenLayers.Control.DrawFeature(lyr, OpenLayers.Handler.Point, {'displayClass': 'olControlDrawFeaturePoint', 'title': 'Draw Points'});
  };
  /* if is_collection==true and collection_type=='Any', we should
   * provide a widget that allows choosing the type of feature to
   * add... but that'd take a lot more work. Possible example to draw
   * on: http://openlayers.org/dev/examples/snapping.html
   * For now, just assume we want MultiPolygons.
   */
  if (draw_ctl == undefined) {
    draw_ctl = new OpenLayers.Control.DrawFeature(lyr, OpenLayers.Handler.Polygon, {'displayClass': 'olControlDrawFeaturePolygon', 'title': 'Draw Polygons'});
  };
  if ({{module}}.is_collection )  {
      draw_ctl.multi = true;
  };
  if ({{ module }}.modifiable){
    var mod = new OpenLayers.Control.ModifyFeature(lyr, {'displayClass': 'olControlModifyFeature', 'title': 'Modify'});
    {{ module }}.controls = [nav, draw_ctl, mod];
  } else {
    if(!lyr.features.length){
      {{ module }}.controls = [nav, draw_ctl];
    } else {
      {{ module }}.controls = [nav];
    }
  }
};
{{ module }}.init = function(){
    {% block map_options %}// The options hash, w/ zoom, resolution, and projection settings.
    var options = {
{% autoescape off %}{% for item in map_options.items %}      '{{ item.0 }}' : {{ item.1 }}{% if not forloop.last %},{% endif %}
{% endfor %}{% endautoescape %}    };{% endblock %}
    // The admin map for this geometry field.
    {{ module }}.map = new OpenLayers.Map('{{ id }}_map', options);
    // Base Layer
    {{ module }}.layers.base = {% block base_layer %}new OpenLayers.Layer.WMS( "{{ wms_name }}", "{{ wms_url }}", {layers: '{{ wms_layer }}' {{ wms_options|safe }} }  );{% endblock %}
    {{ module }}.map.addLayer({{ module }}.layers.base);
    {% block extra_layers %}{% endblock %}
    {% if is_linestring %}OpenLayers.Feature.Vector.style["default"]["strokeWidth"] = 3; // Default too thin for linestrings. {% endif %}
    {{ module }}.layers.vector = new OpenLayers.Layer.Vector(" {{ field_name }}");
    {{ module }}.map.addLayer({{ module }}.layers.vector);
    // Read WKT from the text field.
    var wkt = document.getElementById('{{ id }}').value;
    if (wkt){
      // After reading into geometry, immediately write back to
      // WKT <textarea> as EWKT (so that SRID is included).
      var admin_geom = {{ module }}.read_wkt(wkt);
      {{ module }}.write_wkt(admin_geom);
      {{ module }}.layers.vector.addFeatures([admin_geom]);
      var bounds = admin_geom.geometry.getBounds();
      {{ module }}.map.zoomToExtent(bounds);
      if ({{ module }}.is_point){
          {{ module }}.map.zoomTo({{ point_zoom }});
      };
    } else {
      {{ module }}.map.setCenter(new OpenLayers.LonLat({{ default_lon }}, {{ default_lat }}), {{ default_zoom }});
    }
    // This allows editing of the geographic fields -- the modified WKT is
    // written back to the content field (as EWKT, so that the ORM will know
    // to transform back to original SRID).
    {{ module }}.layers.vector.events.on({"featuremodified" : {{ module }}.modify_wkt});
    {{ module }}.layers.vector.events.on({"featureadded" : {{ module }}.add_wkt});
    {% block controls %}
    // Map controls:
    // Add geometry specific panel of toolbar controls
    {{ module }}.getControls({{ module }}.layers.vector);
    {{ module }}.panel.addControls({{ module }}.controls);
    {{ module }}.map.addControl({{ module }}.panel);
    {{ module }}.addSelectControl();
    // Then add optional visual controls
    {% if mouse_position %}{{ module }}.map.addControl(new OpenLayers.Control.MousePosition());{% endif %}
    {% if scale_text %}{{ module }}.map.addControl(new OpenLayers.Control.Scale());{% endif %}
    {% if layerswitcher %}{{ module }}.map.addControl(new OpenLayers.Control.LayerSwitcher());{% endif %}
    // Then add optional behavior controls
    {% if not scrollable %}{{ module }}.map.getControlsByClass('OpenLayers.Control.Navigation')[0].disableZoomWheel();{% endif %}
    {% endblock %}
    if (wkt){
      if ({{ module }}.modifiable){
        {{ module }}.enableEditing();
      }
    } else {
      {{ module }}.enableDrawing();
    }
};

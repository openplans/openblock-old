var map, layer, select, select_vector, newsitems, bounds, selectControl, style;

if (jQuery.browser.msie) {

  jQuery(window).load(function () {
    _onload();
  });
} else {
  jQuery(document).ready(function () {
    _onload();
  });
}

function _onload() {
  loadMap();
}

var options = {
  projection: new OpenLayers.Projection("EPSG:900913"), // meters
  displayProjection: new OpenLayers.Projection("EPSG:4326"), // lat/lon
  units: "m",
  numZoomLevels: 19,
  maxResolution: 156543.03390625,
  // Bounds of whole world.
  maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34)
};

function loadNewsItems(params) {
  if (!params) {
    params = {};
  }
  newsitems = new OpenLayers.Layer.Vector("NewsItems", {
    projection: map.displayProjection,
    strategies: [
    new OpenLayers.Strategy.Fixed(), new OpenLayers.Strategy.Cluster()],
    protocol: new OpenLayers.Protocol.HTTP({
      url: "http://fixcity.org/newsitems/search.kml",
      params: params,
      format: new OpenLayers.Format.KML()
    }),
    styleMap: new OpenLayers.StyleMap({
      "default": style,
      "select": {
        fillColor: "#ff9e73",
        strokeColor: "#80503b"
      }
    })
  });
  return newsitems;
};

function loadMap() {
  map = new OpenLayers.Map('detailmap', options);

  var osm = new OpenLayers.Layer.WMS("OpenStreetMap", "http://maps.opengeo.org/geowebcache/service/wms", {
    layers: "openstreetmap",
    format: "image/png",
    bgcolor: '#A1BDC4'
  },
  {
    wrapDateLine: true
  });

  style = new OpenLayers.Style({
    pointRadius: "${radius}",
    externalGraphic: "${url}"
  },
  {
    context: {
      url: "/images/news-cluster-icon.png",
      radius: function (feature) {
        return Math.min(feature.attributes.count * 2, 8) + 5;
      }
    }
  });


   // NYC:
   //var bounds = new OpenLayers.Bounds(-74.047185, 40.679648, -73.907005, 40.882078);
  // Boston... need better coords, got this empirically.
  var bounds = new OpenLayers.Bounds(-71.16, 42.30, -71.02, 42.41);
  bounds.transform(map.displayProjection, map.projection);
  newsitems = loadNewsItems();
  map.addLayers([osm, newsitems]);
  map.zoomToExtent(bounds);
}


var createOutlinedLayer = function(url) {
    var style = new OpenLayers.Style({
            fillOpacity: 0,
            strokeWidth: 1,
            strokeColor: "#f35824"
        });
    var outlineLayer = new OpenLayers.Layer.Vector("Outline", {
            projection: map.displayProjection,
            strategies: [
                         new OpenLayers.Strategy.Fixed()
                         ],
            protocol: new OpenLayers.Protocol.HTTP({
                    url: url,
                    params: {},
                    format: new OpenLayers.Format.KML()
                }),
            styleMap: new OpenLayers.StyleMap({
                    "default": style
                })
        });
    outlineLayer.events.on({
            loadend: function(evt) {
                var layer = evt.object;
                var bounds = layer.getDataExtent();
                map.zoomToExtent(bounds);
            }
        });
    return outlineLayer;
};

var updateMapFn = function() {
  var params = {};
    // remove all non base layers
    for (var i = map.layers.length-1; i >= 1; i--) {
        map.removeLayer(map.layers[i]);
    }
    // and an additional layer for the outline of the boro/cb
    var url;
    if (params.cb == "0") {
        // borough query
        url = '/borough/' + params.boro + '.kml';
    } else {
        url = '/communityboard/' + params.cb + '.kml';
    }
    map.addLayer(createOutlinedLayer(url));
    // the layer for all newsitems
    map.addLayer(loadNewsItems(params));
};

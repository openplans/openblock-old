/* Re-usable map for (hopefully) all pages needing a map on
 * demo.openblockproject.org.
 *
 * This takes a similar approach to the maps on everyblock.com: since
 * the bounds of the area we care about are fixed at page load time,
 * we can avoid the overhead of XHR requests by embedding the feature
 * clusters for all zoom levels as (generated) javascript on each page
 * that uses this map.
 *
 */

var map, layer, select, select_vector, newsitems, bounds, selectControl, style;
if (jQuery.browser.msie) {
    jQuery(window).load(function() {
        _onload();
    });
} else {
    jQuery(document).ready(function() {
        _onload();
    });
}
function _onload() {
    loadMap();
}
var options = {
    projection: new OpenLayers.Projection("EPSG:900913"), // meters
    displayProjection: new OpenLayers.Projection("EPSG:4326"), // lon/lat
    units: "m",
    // TODO: actually use the zoom levels specified in all_bunches
    numZoomLevels: 19,
    // Max boundaries = whole world.
    maxResolution: 156543.03390625,
    maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34)
};

function loadNewsItems() {
    newsitems = new OpenLayers.Layer.Markers("NewsItems", {
        projection: map.displayProjection
    });
    var scale = "614400"; // TODO: get scale from current zoom level
    var my_bunches = all_bunches[scale];
    var icon = new OpenLayers.Icon("/images/news-cluster-icon.png");

    for (i = 0; i < my_bunches.length ; i++) {
        var bunch_center = my_bunches[i][1];
        var xy = new OpenLayers.LonLat(bunch_center[0], bunch_center[1]);
        xy.transform(map.displayProjection, map.projection);
        var marker = new OpenLayers.Marker(xy, icon.clone());
        newsitems.addMarker(marker);
    }
    return newsitems;
};

function loadMap() {
    map = new OpenLayers.Map('detailmap', options);
    var osm = new OpenLayers.Layer.WMS("OpenStreetMap", "http://maps.opengeo.org/geowebcache/service/wms", {
        layers: "openstreetmap",
        format: "image/png",
        bgcolor: '#A1BDC4'
    }, {
        wrapDateLine: true
    });
    style = new OpenLayers.Style({
        //pointRadius: "${radius}",
        //externalGraphic: "${url}"
    }, {
        context: {
            url: "/images/news-cluster-icon.png",
            radius: function(feature) {
                return Math.min(feature.attributes.count * 2, 8) + 5;
            }
        }
    });
    // NYC:
    //var bounds = new OpenLayers.Bounds(-74.047185, 40.679648, -73.907005, 40.882078);
    // Boston... need better coords, got this empirically.
    var newsitems = loadNewsItems();
    map.addLayers([osm, newsitems]);
    newsitems.setVisibility(true);
//    newsitems.refresh();
    var center = new OpenLayers.LonLat(-71.061667, 42.357778);
    center.transform(map.displayProjection, map.projection);
    map.setCenter(center, 12);
    //map.setCenter(newsitems.features[0].geometry.getBounds().getCenterLonLat(), 18);
}

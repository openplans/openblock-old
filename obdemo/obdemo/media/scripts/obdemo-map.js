/* Re-usable map for (hopefully) all pages needing a map on
 * demo.openblockproject.org.
 *
 * Rewritten to use a more conventional OpenLayers clustering approach:
 * we use OL's native clustering support, and add a view on the server
 * that serves un-clustered news items via AJAX.
 */
var map, newsitems, style;

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
    newsitems = new OpenLayers.Layer.Vector("NewsItems", {
        projection: map.displayProjection,
        strategies: [
            new OpenLayers.Strategy.Fixed(),
            new OpenLayers.Strategy.Cluster()
        ],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "/api/newsitems.geojson/", /* WILL CHANGE */
            params: {},
            format: new OpenLayers.Format.GeoJSON()
        }),
        styleMap: new OpenLayers.StyleMap({
            "default": style
        })
    });
    // var scale = "614400"; // TODO: get scale from current zoom level
    // var my_bunches = all_bunches[scale];
    // var icon = new OpenLayers.Icon("/images/news-cluster-icon.png");
    // for (i = 0; i < my_bunches.length ; i++) {
    //     var bunch_center = my_bunches[i][1];
    //     var xy = new OpenLayers.LonLat(bunch_center[0], bunch_center[1]);
    //     xy.transform(map.displayProjection, map.projection);
    //     var marker = new OpenLayers.Marker(xy, icon.clone());
    //     newsitems.addMarker(marker);
    // }

    // ---------------- Popups ------------------------------//
    var featureSelected = function (feature) {
        var cluster = feature.cluster;
        var firstFeature = cluster[0];
        var featureHtml = ('<div>' + firstFeature.attributes.title +  '</div>');
        var popup = new OpenLayers.Popup.FramedCloud(
            null, feature.geometry.getBounds().getCenterLonLat(),
            null, featureHtml, {
                size: new OpenLayers.Size(1, 1),
                offset: new OpenLayers.Pixel(0, 0)
            },
            true, function () {
                selectControl.unselect(feature);
            });
        feature.popup = popup;
        map.addPopup(popup);
        if (cluster.length > 1) {
            // Add next/previous nav links to the popup.
            var navHtml = '<div><a class="popupnav prev" href="#">prev</a>&nbsp;<a class="popupnav next" href="#">next</a></div>';
            var clusterIdx = 0;
            var content = popup.contentDiv;
            var foo = $(content);
            $(content).append($(navHtml)); // works in fixcity code but not here??
            var prev = $(content).find('a.popupnav.prev');
            var next = $(content).find('a.popupnav.next');

            // Clicking next or previous replaces the nav links html.
            var replaceHtml = function (f) {
                $(content).find('a:first').attr('href', '/XXX/' + f.fid);
                //var thumb = (f.attributes.thumbnail != null) ? f.attributes.thumbnail.value : '/site_media/img/default-rack.jpg';
                //$(content).find('img').attr('src', thumb);
            };
            prev.click(function (e) {
                e.preventDefault();
                clusterIdx = (clusterIdx == 0) ? cluster.length - 1 : clusterIdx - 1;
                replaceHtml(cluster[clusterIdx]);
                // popup.draw();
            });
            next.click(function (e) {
                e.preventDefault();
                clusterIdx = (clusterIdx == cluster.length - 1) ? 0 : clusterIdx + 1;
                replaceHtml(cluster[clusterIdx]);
               // popup.draw();
            });
        }
    };
    var featureUnselected = function (feature) {
        map.removePopup(feature.popup);
        feature.popup.destroy();
        feature.popup = null;
    };
    var selectControl = new OpenLayers.Control.SelectFeature(newsitems, {
        onSelect: featureSelected,
        onUnselect: featureUnselected
    });
    map.addControl(selectControl);
    selectControl.activate();
    // ---------------- End of Popups code -------------------------//

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
        pointRadius: "${radius}",
        fillColor: "#edbc22",
        fillOpacity: 0.7,
        strokeColor: "#cc6633",
        strokeWidth: 2,
        strokeOpacity: 0.8,
        label: "${getlabel}",
        fontColor: "#ffffff",
        fontSize: 14
        }, {
        context: {
            radius: function(feature) {
                return 8 + Math.min(feature.attributes.count * 1.8, 20);
            },
            getlabel: function(feature) {
                return feature.attributes.count;
            }
        }
    });
    var newsitems = loadNewsItems();
    map.addLayers([osm, newsitems]);
    newsitems.setVisibility(true);
    //newsitems.refresh();
    var center = new OpenLayers.LonLat(-71.061667, 42.357778);
    center.transform(map.displayProjection, map.projection);
    map.setCenter(center, 12);
    //map.setCenter(newsitems.features[0].geometry.getBounds().getCenterLonLat(), 18);
}

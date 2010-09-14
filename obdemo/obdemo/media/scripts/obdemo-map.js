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
    numZoomLevels: 19,
    // Max boundaries = whole world.
    maxResolution: 156543.03390625,
    maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34)
};

// TODO: Update this to limit the schemas we show, eg: newsitem_params['schema'] = 'events'
var newsitem_params = {pid: pid}; // expect pid to be set prior to this script

function loadNewsItems() {
    newsitems = new OpenLayers.Layer.Vector("NewsItems", {
        projection: map.displayProjection,
        strategies: [
            new OpenLayers.Strategy.Fixed(),
            new OpenLayers.Strategy.Cluster()
            ],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "/api/newsitems.geojson/", /* WILL CHANGE */
            params: newsitem_params,
            format: new OpenLayers.Format.GeoJSON()
        }),
        styleMap: new OpenLayers.StyleMap({
            "default": style
        })
    });
    // ---------------- Popups ------------------------------//
    var featureSelected = function(feature) {
        var cluster = feature.cluster;
        var clusterIdx = 0;
        var firstFeature = cluster[0];
        var featureHtml = firstFeature.attributes.popup_html;
        var popup = new OpenLayers.Popup.FramedCloud(
        null, feature.geometry.getBounds().getCenterLonLat(), null, featureHtml, {
            size: new OpenLayers.Size(1, 1),
            offset: new OpenLayers.Pixel(0, 0)
        }, true, function() {
            selectControl.unselect(feature);
        });
        feature.popup = popup;
        map.addPopup(popup);
        if (cluster.length > 1) {
            // Add next/previous nav links to the popup.
            var navHtml = '<div><a class="popupnav prev" href="#">prev</a>&nbsp;<a class="popupnav next" href="#">next</a></div>';
            var content = popup.contentDiv;
            $(content).append(navHtml);
            var prev = $(content).find('a.popupnav.prev');
            var next = $(content).find('a.popupnav.next');
            // Clicking next or previous replaces the nav links html.
            var replaceHtml = function(f) {
                // Fixme: this comes up empty. replaceWith() isn't right?
                $(content).find('.newsitem').replaceWith(f.attributes.popup_html);
                // todo: re-insert the nav
                //$(content).find('a:first').attr('href', '/XXX/' + f.fid);
            };
            prev.click(function(e) {
                e.preventDefault();
                clusterIdx = (clusterIdx == 0) ? cluster.length - 1 : clusterIdx - 1;
                replaceHtml(cluster[clusterIdx]);
                // popup.draw();
            });
            next.click(function(e) {
                e.preventDefault();
                clusterIdx = (clusterIdx == cluster.length - 1) ? 0 : clusterIdx + 1;
                replaceHtml(cluster[clusterIdx]);
                // popup.draw();
            });
        }
    };
    var featureUnselected = function(feature) {
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
                return 8 + Math.min(feature.attributes.count * 1.2, 14);
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

    // map_center is expected to be set in the enclosing template,
    // like so:
    //var map_center = new OpenLayers.LonLat(-71.061667, 42.357778);
    // var map_zoom = 12;

    if (typeof(map_center) != "undefined") {
        map_center.transform(map.displayProjection, map.projection);
        map.setCenter(map_center, map_zoom);
    };
    // Or you can set map_bounds.
    if (typeof(map_bounds) != "undefined") {
        map_bounds.transform(map.displayProjection, map.projection);
        map.zoomToExtent(map_bounds);
    };
}

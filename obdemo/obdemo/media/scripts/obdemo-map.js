/* Re-usable map for (hopefully) all pages needing a map on
 * demo.openblockproject.org.
 *
 * Rewritten to use a more conventional OpenLayers clustering approach:
 * we use OL's native clustering support, and add a view on the server
 * that serves un-clustered news items via AJAX.
 */

/*
 * This map expects the following variables to be set:
 *
 * pid (OPTIONAL) - a place ID like 'b:12.1' (see
 * ebpub.utils.view_utils for more info).
 *
 * place_type (OPTIONAL) - a type like 'neighborhood' or 'zip'.  If
 * provided, place_slug must also be provided, and we will will draw
 * boundaries around the given place.
 *
 * place_slug (required iff place_type is set) - name of the place,
 * eg. 'downtown', used for constructing a place URL.
 *
 * schema_slug (OPTIONAL) - slug of schema to filter on.
 *
 * newsitems_ajax_url (OPTIONAL) - url to use for requesting features.
 *
 * map_bounds - an OpenLayers.Bounds() defining the default boundaries.
 * If set, you don't need map_center or map_zoom.
 *
 * map_center - an OpenLayers.LonLat(). If set, you also need map_zoom.
 *
 * map_zoom - zoom level. Required if you set map_center.
 */
var map, newsitems, style, borderstyle;
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

function loadNewsItems() {
    if (typeof(newsitems_ajax_url == "undefined")) {
        var newsitems_ajax_url = "/api/newsitems.geojson/"; /* WILL CHANGE */
    };
    // TODO: Update this to limit the schemas we show, eg: newsitem_params['schema'] = 'events'

    // Expect pid to be set globally prior to calling this function.
    var newsitem_params = {pid: '', schema: ''};
    if (typeof(pid) != 'undefined') {
        newsitem_params.pid = pid;
    };
    if (typeof(schema_slug) != 'undefined') {
        newsitem_params.schema = schema_slug;
    };

    var newsitems = new OpenLayers.Layer.Vector("NewsItems", {
        projection: map.displayProjection,
        strategies: [
            new OpenLayers.Strategy.Fixed(),
            new OpenLayers.Strategy.Cluster({'distance': 26})
            ],
        protocol: new OpenLayers.Protocol.HTTP({
            url: newsitems_ajax_url,
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
            null, feature.geometry.getBounds().getCenterLonLat(), null, featureHtml,
            {size: new OpenLayers.Size(1, 1), offset: new OpenLayers.Pixel(0, 0)},
            true, // closeBox.
            function() {
                // Callback for closing box.
                selectControl.unselect(feature);
            }
        );
        feature.popup = popup;
        map.addPopup(popup);
        if (cluster.length > 1) {
            // Add next/previous nav links to the popup.
            var navHtml = '<span class="popupnav"><a class="popupnav prev" href="#">&larr;prev</a>&nbsp;&nbsp;<a class="popupnav next" href="#">next&rarr;</a></span>';
            var content = popup.contentDiv;
            // I like nav links at top and bottom for convenience.
            $(content).prepend(navHtml);
            $(content).append(navHtml);
            popup.updateSize();
            var prev = $(content).find('a.popupnav.prev');
            var next = $(content).find('a.popupnav.next');
            // Clicking next or previous replaces the nav links html.
            var replaceHtml = function(f) {
                $(content).find('.newsitem').replaceWith(f.attributes.popup_html);
            };
            prev.click(function(e) {
                e.preventDefault();
                clusterIdx = (clusterIdx == 0) ? cluster.length - 1 : clusterIdx - 1;
                replaceHtml(cluster[clusterIdx]);
            });
            next.click(function(e) {
                e.preventDefault();
                clusterIdx = (clusterIdx == cluster.length - 1) ? 0 : clusterIdx + 1;
                replaceHtml(cluster[clusterIdx]);
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

function loadLocationBorder(place_type, place_slug) {
    borderstyle = new OpenLayers.Style({
        fillColor: "#cc0022",
        fillOpacity: 0.05,
        strokeColor: "#bb0000",
        strokeWidth: 2,
        strokeOpacity: 0.6,
        label: ""
    }, {
        context: {
        }
    });
    var location = new OpenLayers.Layer.Vector("LocationBorder", {
        projection: map.displayProjection,
        strategies: [
            new OpenLayers.Strategy.Fixed()
            ],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "/locations/" + place_type + "/" + place_slug + "/place.kml",
            params: {},
            format: new OpenLayers.Format.KML()
        }),
        styleMap: new OpenLayers.StyleMap({
            "default": borderstyle
        })
    });
    return location;
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
	        // Size of cluster, in pixels.
                return 8 + Math.min(feature.attributes.count * 0.7, 14);
            },
            getlabel: function(feature) {
                return feature.attributes.count;
            }
        }
    });
    var newsitems = loadNewsItems();
    map.addLayers([osm]);
    if (typeof(place_type) != "undefined" && Boolean(place_type)) {
        var locationborder = loadLocationBorder(place_type, place_slug);
        map.addLayers([locationborder]);
        locationborder.setVisibility(true);
    };
    map.addLayers([newsitems]);
    newsitems.setVisibility(true);
    //newsitems.refresh();

    if (typeof(map_center) != "undefined") {
        map_center.transform(map.displayProjection, map.projection);
        map.setCenter(map_center, map_zoom);
    };
    if (typeof(map_bounds) != "undefined") {
        map_bounds.transform(map.displayProjection, map.projection);
        map.zoomToExtent(map_bounds);
    };
}

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
  projection: new OpenLayers.Projection("EPSG:900913"),
  displayProjection: new OpenLayers.Projection("EPSG:4326"),
  units: "m",
  numZoomLevels: 19,
  maxResolution: 156543.03390625,
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
  var featureSelected = function (feature) {
    //$('ul#newsitemlist li').removeClass('selected').filter('#newsitem_' + feature.fid).addClass('selected');
    var cluster = feature.cluster;
    var firstFeature = cluster[0];
    // can potentially select multiple newsitems
    $('ul.home-list li').removeClass('selected');
    var homeList = $('ul.home-list');
    for (var i = 0; i < feature.cluster.length; i++) {
      homeList.find('#newsitem_' + feature.cluster[i].fid).addClass('selected');
    }
    //var popup = new FixcityPopup(null, feature.geometry.getBounds().getCenterLonLat(),
    //                             null, ('<div class="newsitem-info"><a href="/newsitems/' + feature.fid + '"><img src="' + ((feature.cluster[0].attributes.thumbnail != null) ? feature.cluster[0].attributes.thumbnail.value : '/site_media/img/default-newsitem.jpg') + '" width="50" /></a><h3><a href="/newsitems/' + feature.fid + '">' + feature.cluster[0].attributes.name + '</a></h3><h4>' + feature.cluster[0].attributes.address + '</h4>' + ((feature.cluster[0].attributes.verified == null) ? '' : '<h5><em>verified</em></h5>') + '</div>'),
    //                             {size: new OpenLayers.Size(1, 1), offset: new OpenLayers.Pixel(-40, 48)},
    //                             true, function() { selectControl.unselect(feature); });
    var featureHtml = ('<div class="newsitem-info"><a href="/newsitems/' + firstFeature.fid + '"><img src="' + ((firstFeature.attributes.thumbnail != null) ? firstFeature.attributes.thumbnail.value : '/site_media/img/default-newsitem.jpg') + '" width="50" /></a><h3><a href="/newsitems/' + firstFeature.fid + '">' + firstFeature.attributes.name + '</a></h3><h4>' + firstFeature.attributes.address + '</h4>' + '<h5>' + firstFeature.attributes.votes.value + ' votes</h5>' + ((firstFeature.attributes.verified == null) ? '' : '<h5><em>verified</em></h5>') + '</div>');
    var popup = new OpenLayers.Popup.FramedCloud(
    null, feature.geometry.getBounds().getCenterLonLat(), null, featureHtml, {
      size: new OpenLayers.Size(1, 1),
      offset: new OpenLayers.Pixel(0, 0)
    },
    true, function () {
      selectControl.unselect(feature);
    });
    feature.popup = popup;
    map.addPopup(popup);
    if (cluster.length > 1) {
      navHtml = '<div><a class="popupnav prev" href="#">prev</a>&nbsp;<a class="popupnav next" href="#">next</a></div>';
      var clusterIdx = 0;
      var content = popup.contentDiv;
      $(content).append($(navHtml));
      var prev = $(content).find('a.popupnav.prev');
      var next = $(content).find('a.popupnav.next');
      var replaceHtml = function (f) {
        $(content).find('a:first').attr('href', '/newsitems/' + f.fid);
        var thumb = (f.attributes.thumbnail != null) ? f.attributes.thumbnail.value : '/site_media/img/default-newsitem.jpg';
        $(content).find('img').attr('src', thumb);
        $(content).find('h3 a').attr('href', '/newsitems/' + f.fid);
        $(content).find('h3 a').text(f.attributes.name);
        $(content).find('h4').text(f.attributes.address);
        $(content).find('h5').remove();
        $(content).find('h4').after('<h5>' + f.attributes.votes.value + ' votes</h5>');
        if (f.attributes.verified != null) {
          $(content).find('h5').after('<h5><em>verified</em></h5>');
        }
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
  // selectControl = new OpenLayers.Control.SelectFeature(newsitems, {
  //   onSelect: featureSelected,
  //   onUnselect: featureUnselected
  // });
  // map.addControl(selectControl);
  // selectControl.activate();
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


  var bounds = new OpenLayers.Bounds(-8234063.45026893, 4968638.33081464, -8230209.19302436, 4973585.50729644);
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



/***************************************************/

function _obapi(path) {
    var OB_API_ROOT = '/api/dev1';
    return OB_API_ROOT + path;
}

function _report_error(error) {
    /* FIXME */ 
}

var OpenblockCluster = OpenLayers.Class(OpenLayers.Strategy.Cluster, {
    /* inherits fro the OpenLayers.Strategy.Cluster class and 
     * adds a pre-reclustering notification and splitting of clusters
     * based on characteristics of a feature.
     * 
     * options: 
     * 
     * clusterSignature: a function accepting a feature and returning a string that 
     *   characerizes the cluster 'type' it belongs to.
     */
    events: null,

    EVENT_TYPES: ["beforecluster"],
                  
    initialize: function(options) {
        OpenLayers.Strategy.Cluster.prototype.initialize.call(this, options);
        this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);
        
        if (typeof(options.eventListeners) != "undefined") {
            this.events.on(options.eventListeners)
        }
        
        if (typeof(options.clusterSignature) != "undefined") {
            this.clusterSignature = options.clusterSignature;
        }
        else {
            this.clusterSignature = function(feature) {
                return null;
            };
        }
    },

    cluster: function(event) {
        if((!event || event.zoomChanged) && this.features) {
            /* if this will trigger a reclustering */
            this.events.triggerEvent("beforecluster", {'layer': this.layer});
        }
        return OpenLayers.Strategy.Cluster.prototype.cluster.call(this, event);
    },
    
    shouldCluster: function(cluster, feature) {
        return OpenLayers.Strategy.Cluster.prototype.shouldCluster.call(this, cluster, feature) && 
               this.clusterSignature(feature) == cluster.signature;
    }, 
    
    createCluster: function(feature) {
        var cluster = OpenLayers.Strategy.Cluster.prototype.createCluster.call(this, feature);
        cluster.signature = this.clusterSignature(feature);
        return cluster;
    }
});


var OBMap = function(options) {
    /*
    * options: 
    *
    * center : pair of floating point values [lon, lat]
    * zoom : floating point value representing map scale
    * bounds : list of 4 floating point values [minlon,minlat,maxlon,maxlat]
    * locations : list of layer configurations
    * layers : list of layer configurations
    * baselayer_type : one of 'google', 'wms'
    * wms_url : if using a WMS baselayer, url 
    *
    * layer configuration is an object with the follow attributes: 
    *  
    * url: url to a geojson layer 
    * params: dictionary of parameters to use when fetching the layer 
    * title: string representing layer title
    * visible: boolean whether the layer is initially visible
    *
    */
    this.options = options; 
    this._initBasicMap();
    this._configurePopup();
    this._configureLayers();
    this.popup = null; 
    this.clusterDistance = 38;
};

/* default map options */
OBMap.prototype.map_options = {
    projection: new OpenLayers.Projection("EPSG:900913"), // meters
    displayProjection: new OpenLayers.Projection("EPSG:4326"), // lon/lat
    units: "m",
    numZoomLevels: 19,
    // Max boundaries = whole world.
    maxResolution: 156543.03390625,
    maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34)
};

OBMap.prototype.refresh = function() {
    for (var i=0; i < this.map.layers.length; i++) {
        var layer = this.map.layers[i];
        if (layer.refresh && typeof(layer.refresh) == "function") {
            layer.refresh();
        }
    }
};

OBMap.prototype._initBasicMap = function() {
    /* initialize the map with base layer, bounds and 
     * other common settings.
     */
    this.map = new OpenLayers.Map("detailmap", this.map_options);
    if ( this.options.baselayer_type == "google" ) {
        var google = new OpenLayers.Layer.Google("Google", {
            wrapDateLine: true, sphericalMercator: true,
            displayInLayerSwitcher: false
        });
        this.map.addLayers([google]);
    }
    else if ( this.options.baselayer_type == "wms" ) {
        var osm = new OpenLayers.Layer.WMS("OpenStreetMap", this.options.wms_url, {
             layers: "openstreetmap",
             format: "image/png",
             bgcolor: "#A1BDC4"
        }, {
             wrapDateLine: true,
             displayInLayerSwitcher: false
        });
        this.map.addLayers([osm]);
    }
    else {
        alert("Map type must be one of 'wms' or 'google', got " + this.options.baselayer_type);
    }

    if (typeof(this.options.center) != "undefined") {
        var map_center = new OpenLayers.LonLat(this.options.center[0], this.options.center[1]); 
        map_center.transform(this.map.displayProjection, this.map.projection);
        this.map.setCenter(map_center, this.options.zoom);
    }
    if (typeof(this.options.bounds) != "undefined") {
        var bbox = this.options.bounds;
        var map_bounds = new OpenLayers.Bounds(bbox[0],bbox[1],bbox[2],bbox[3]);
        map_bounds.transform(this.map.displayProjection, this.map.projection);
        this.map.zoomToExtent(map_bounds);
    }
};

OBMap.prototype._configureLayers = function() {
    if (typeof(this.options.locations) != 'undefined') {
        for (var i = 0; i < this.options.locations.length; i++) {
            this.loadLocationBorder(this.options.locations[i]);
        }
    }
    if (typeof(this.options.layers) != 'undefined') {
        for (var i = 0; i < this.options.layers.length; i++) {
            this.loadFeatureLayer(this.options.layers[i]);
        }
    }
};

OBMap.prototype.loadLocationBorder = function(layerConfig) {
    var borderstyle = new OpenLayers.Style({
        fillColor: "#cc0022",
        fillOpacity: 0.05,
        strokeColor: "#bb0000",
        strokeWidth: 2,
        strokeOpacity: 0.6,
        label: ""
    }, {
        context: {}
    });
    var location = new OpenLayers.Layer.Vector("LocationBorder", {
        projection: this.map.displayProjection,
        displayInLayerSwitcher: false,
        visibility: layerConfig.visible,
        strategies: [
            new OpenLayers.Strategy.Fixed()
            ],
        protocol: new OpenLayers.Protocol.HTTP({
            url: layerConfig.url,
            params: layerConfig.params,
            format: new OpenLayers.Format.GeoJSON()
        }),
        styleMap: new OpenLayers.StyleMap({
            "default": borderstyle
        })
    });
    this.map.addLayers([location]);
    return location;
};

OBMap.prototype.getLayerStyleMap = function() {
    /* returns the default StyleMap for news / place layers */
    var defaultStrokeColor, defaultFillColor; 
    if (this.options.baselayer_type == "google") {
        defaultStrokeColor = "#0041F4";
        defaultFillColor = "#00A66C";
    } else {
        defaultStrokeColor = "#CC6633";
        defaultFillColor = "#EDBC22";
    }

    var _hasIcon = function(feature) {
        return typeof(feature.cluster[0].attributes.icon) != 'undefined' &&
               feature.cluster[0].attributes.icon;  
    };
    
    var defaultStyle = new OpenLayers.Style({
        pointRadius: "${radius}",
        externalGraphic: "${iconUrl}",
        fillColor: "${fillColor}",
        fillOpacity: 0.8,
        strokeColor: defaultStrokeColor,
        strokeWidth: 2,
        strokeOpacity: 0.8,
        label: "",
        fontColor: "#ffffff",
        fontSize: 14
    }, {
        context: {
            radius: function(feature) {
                // Size of cluster, in pixels.
                if (_hasIcon(feature)) {
                    // icon size bonus for number of features in the cluster. 
                    // 0 for 1, growing logarithmically to a max of 8 for 10 features.
                    return 10 + Math.min(3.474*Math.log(feature.attributes.count), 8);
                }
                else {
                    // colored circle
                    return 8 + Math.min(feature.attributes.count * 0.7, 14);
                }
            },
            iconUrl: function(feature) {
                if (_hasIcon(feature)) {
                    return feature.cluster[0].attributes.icon;
                }
                else {
                    return '';
                }
            },
            fillColor: function(feature) {
                if (typeof(feature.cluster[0].attributes.color) != 'undefined' &&
                    feature.cluster[0].attributes.color) {
                    return feature.cluster[0].attributes.color;
                }
                else {
                    return defaultFillColor;
                }
            }
       }
    });

    return new OpenLayers.StyleMap({
        "default": defaultStyle,
        "select": defaultStyle
    });
};

OBMap.prototype.loadFeatureLayer = function(layerConfig) {

    var layer = new OpenLayers.Layer.Vector(layerConfig['title'], {
        allowSelection: true,
        projection: this.map.displayProjection,
        visibility: layerConfig['visible'],
        strategies: [
            new OpenLayers.Strategy.BBOX(
                    {
                        ratio: 1.75,
                        resFactor: 3
                    }
                ),
            new OpenblockCluster({
                distance: this.clusterDistance,
                clusterSignature: function(feature) {
                    // separate based on icon, then color
                    if (typeof(feature.attributes.icon) != 'undefined' && feature.attributes.icon) {
                        return $.trim(feature.attributes.icon).toLowerCase();
                    }
                    else if (typeof(feature.attributes.color) != 'undefined' && feature.attributes.color) {
                        return $.trim(feature.attributes.color).toLowerCase(); 
                    }
                    else {
                        return null;
                    }
                }
            })
            ],
        protocol: new OpenLayers.Protocol.HTTP({
            url: layerConfig['url'],
            params: layerConfig['params'],
            format: new OpenLayers.Format.GeoJSON()
        }),
        styleMap: this.getLayerStyleMap()
    });
    this.map.addLayers([layer]);
};


OBMap.prototype.loadAllNewsLayers = function() {
    /* load news item types, create a layer for each */

    jQuery.ajax({
        url: _obapi('/items/types.json'),
        dataType: 'json',
        context: this,
        success: function(data, status, request) {
            for (var slug in data) {
                if (data.hasOwnProperty(slug)) {
                    var itemType = data[slug];                    
                    var layerConfig = {
                        title:  itemType["plural_name"],
                        url:    _obapi('/items.json'),
                        params: {'type': slug, 'limit': 100},
                        visible: true
                    };
                    this.loadFeatureLayer(layerConfig);
                }
            }
        },
        error: function(request, status, error) {
            _report_error('An error occurred loading news item types.');
        }
    });
};

OBMap.prototype.loadAllPlaceLayers = function() {
    /* load place types, create a layer for each */
    jQuery.ajax({
        url: _obapi('/places/types.json'),
        dataType: 'json',
        context: this,
        success: function(data, status, request) {
            for (var slug in data) {
                if (data.hasOwnProperty(slug)) {
                    var itemType = data[slug];
                    var layerConfig = {
                        title: itemType["plural_name"],
                        url: _obapi('/places/' + slug +'.json'),
                        params: {'limit': 100},
                        visible: false
                    };
                    this.loadFeatureLayer(layerConfig);
                }
            }
        },
        error: function(request, status, error) {
            _report_error('An error occurred loading news item types.');
        }
    });
};


OBMap.prototype._featureSelected = function(feature) {
    // close any existing popup
    this._closePopup();
    
    var cluster = feature.cluster;
    var clusterIdx = 0;
    var firstFeature = cluster[0];
    var initialHTML = '<div class="popup-container"><div class="popup-content"></div></div>';
    
    var theMap = this;
    var popup = new OpenLayers.Popup.FramedCloud(
        null, feature.geometry.getBounds().getCenterLonLat(), null, initialHTML,
        {size: new OpenLayers.Size(1, 1), offset: new OpenLayers.Pixel(0, 0)},
        true, // closeBox.
        function() {
            theMap._closePopup();
            theMap.selectControl.unselect(feature);
        }
    );
    popup.focalFeature = firstFeature;
    popup.forCluster = feature;
    popup.contentDiv.className = "openblockFramedCloudPopupContent";
    popup.maxSize = new OpenLayers.Size(320, 320);
    popup.panMapIfOutOfView = true;
    this.popup = popup;
    this.map.addPopup(popup);
    
    
    popup.checkPosition = function() {
        /* determine where the popup should point.  If the new position 
         * is still within the radius of the cluster, don't move.  It 
         * may be far away though if the map was zoomed -- if this is the 
         * case, move the popup over the new location.
         */
        var clonlat = this.forCluster.geometry.getBounds().getCenterLonLat();
        var flonlat = this.focalFeature.geometry.getBounds().getCenterLonLat();
        var cpx = this.map.getLayerPxFromLonLat(clonlat);
        var fpx = this.map.getLayerPxFromLonLat(flonlat);
        var dx = cpx.x-fpx.x;
        var dy = cpx.y-fpx.y;
        var squaredDistance = dx*dx+dy*dy;
        if (squaredDistance <= clusterSquaredDistance) {
            // use cluster center
            this.lonlat = clonlat; 
        }
        else {
            // use feature position
            this.lonlat = flonlat;
        }
        this.updatePosition();
    };

    var clusterSquaredDistance = this.clusterDistance*this.clusterDistance;
    var replaceHtml = function(i) {
        var f = cluster[i];

        var _setContent = function(html) {
            if (clusterIdx == i) { /* if still current */
                popup.focalFeature = f;
                $(popup.contentDiv).find(".popup-content").replaceWith(html);
                if (cluster.length > 1) {
                    $(popup.contentDiv).find("#clusteridx").text(i + 1);
                }
                popup.checkPosition(); 
                popup.updateSize();
                popup.panIntoView();
            }
        };

        var popup_url = '/maps/popup/' + f.attributes.openblock_type + '/' + f.attributes.id;
        jQuery.ajax({
            url: popup_url,
            dataType: 'html',
            success: _setContent,
            error: function(request, status, err) {
                _setContent('<div class="popup-content">'+ status + '</div>');
            }
        });
    };

    if (cluster.length > 1) {
        // Add next/previous nav links to the popup.
        var navHtml = '<div class="popup-nav"><a class="popup-nav-prev" href="#">&larr;prev</a>&nbsp;<span id="clusteridx">1</span>&nbsp;of&nbsp;' + cluster.length
		  + '&nbsp;<a class="popup-nav-next" href="#">next&rarr;</a></div>';
        $(popup.contentDiv).find('.popup-container').append(navHtml);
        var prev = $(popup.contentDiv).find("a.popup-nav-prev");
        var next = $(popup.contentDiv).find("a.popup-nav-next");
        // Clicking next or previous replaces the nav links html.
        prev.click(function(e) {
            e.preventDefault();
            clusterIdx = (clusterIdx == 0) ? cluster.length - 1 : clusterIdx - 1;
            replaceHtml(clusterIdx);
        });
        next.click(function(e) {
            e.preventDefault();
            clusterIdx = (clusterIdx + 1) % cluster.length;
            replaceHtml(clusterIdx);
        });
    }
    replaceHtml(0);
};

OBMap.prototype._featureUnselected = function(feature) {
    if (this.popup && this.popup.forCluster == feature) {
        this._closePopup();
    }
}; 

OBMap.prototype._closePopup = function() {
    if (this.popup != null) {
        this.map.removePopup(this.popup);
        this.popup.destroy();
        this.popup = null;
    }
};

OBMap.prototype._reloadSelectableLayers = function(event) {
    if (event.layer != this.selectControl.layer) {
        var select_layers = [];
        for (var i in this.map.layers) {
            var layer = this.map.layers[i];
            if (typeof(layer.allowSelection) != 'undefined' && 
                layer.allowSelection == true) {
                select_layers.push(layer);
            }
        }
        this.selectControl.setLayer(select_layers);
        this.selectControl.activate();
    }
};




OBMap.prototype._configurePopup = function() {

    this.selectControl = new OpenLayers.Control.SelectFeature([], {
        onSelect: this._featureSelected,
        onUnselect: this._featureUnselected,
        scope: this
    });
    this.map.addControl(this.selectControl);    
    this.map.events.on({'addlayer': this._reloadSelectableLayers,
                        'zoomend': function() {
                            if (this.popup != null) {
                                this.popup.checkPosition();
                            }
                        },
                        'scope': this});
    
};


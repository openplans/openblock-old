============
Introduction
============

Purpose
=======

Support simple widgets, mashups, frontends based on Openblock content and filtering capability.
We would appreciate any feedback you have on how to improve the usefulness and usability of this API.

Caveat
======
This is a preliminary API and may be changed in substantially in future versions.   


See Also
========

The openblock API uses several standards for formats and protocols.  Please see the (externally maintained) documentation focused on the particular formats for more details. These include GeoJSON, Atom and JSONP. Some helpful links:

================== ============================================================
    Format			    URL
------------------ ------------------------------------------------------------
    GeoJSON                   http://geojson.org/
------------------ ------------------------------------------------------------
     Atom                     http://www.atomenabled.org
------------------ ------------------------------------------------------------
     JSONP                    http://en.wikipedia.org/wiki/JSON#JSONP
================== ============================================================


FIXME Examples / Quickstart

============
API Overview
============

URL prefix
==========

All calls to the openblock API referenced in this document are prefixed by::

	/api/dev1/


Support for Cross Domain Access
===============================

To enable widgets and mashups in the browser from domains other than the host OpenBlock instance, the API supports the JSONP.

All portions of the API using the http GET method support JSONP by 
providing the "jsonp" query parameter.


===================
Query API Endpoints
===================


GET [api prefix]
================

Purpose
-------

Test the availability of this version of the API.

Response
--------

================== ============================================================
    Status                                Meaning
------------------ ------------------------------------------------------------
      200             This version of the API is available
------------------ ------------------------------------------------------------
      404             This version of the API is not available
================== ============================================================





GET newsitems.json
==================

Purpose
-------
Retrieve details of a certain set of news items in GeoJSON format.

Parameters
----------
See section "Item Search Parameters"

Response
--------
A GeoJSON FeatureCollection containing a list of GeoJSON features.  Each resulting 
Feature in the collection represents a "NewsItem" that matches the specified search 
criteria.

NewsItem format is specified in the section "NewsItem JSON Format"


Example result: 


GET newsitems.atom
==================

Parameters
----------
See section "Item Search Parameters"

Response
--------
An Atom Feed.  Each resulting Atom Entry in the feed represents a "NewsItem" that 
matches the specified search criteria.

Format is specified in the section "NewsItem Atom Format"


GET locations.json
==================

Purpose
-------
Retrieve a list of predefined locations on the server as a list, 

FIXME just basic info no geom

Response
--------

A json structure describing the list of predefined locations in the system.



GET locations/<locationid>.json
===============================

FIXME This one includes geometry info and details GeoJSON
* skip for now? locations spatially filtered (nearby locations)


FIXME:
* GeoCoder
* List of schema types 
* List of location types 


======================
Item Search Parameters
======================

Search parameters specified select all items that match all criteria simultaneously, eg specifying type="crimereport"&neighborhoods=roxbury selects all items that are of type "crimereport" AND in the Roxbury neighborhood and no other items.

Spatial Filtering
=================

Spatial filters allow the selection of items based on geographic areas. 
At most one spatial filter may be applied per API request.


Predefined Area
---------------

Selects items in some predefined area on the server, eg a neighborhood, zipcode etc. To discover predefined areas
see the endpoint "GET locations.geojson"

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
   locationid      server provided identifier for predefined location.
                   eg: "neighborhoods/roxbury"
================== ==========================================================================


Bounding Circle
---------------

Selects items within some distance of a given point.

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
      center	    <lon>,<lat> comma separated list of 2 floating point 
                    values representing the latitude and longitude of the 
                    center of the circle. eg: center=-71.191153, 42.227865
------------------ --------------------------------------------------------------------------
      radius	   positive floating point maximum distance in meters from the specified 
                   center point
================== ==========================================================================


Other Filters 
=============

FIXME: schema type, date, maybe additional attrs


===================
Formats
===================


NewsItem JSON Format
====================

A NewsItem is represented by a GeoJSON Feature containing: 
a "geometry" attribute representing its specific location, generally a Point.
an "id" attribute containing the url of the item
a "properties" attribute containing details of the news item according to its schema. 

See the GeoJSON specification for additional information on GeoJSON: 
http://geojson.org/geojson-spec.html

FIXME: more detail on attributes


NewsItem Atom Format
====================

generally follows Atom specification
location information is specified with GeoRSS-Simple
Extended schema attributes are specified in "http://openblock.org/ns/0" namespace.

FIXME: more detail


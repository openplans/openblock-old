============
Introduction
============

Purpose
=======

Support simple widgets, mashups, frontends based on Openblock content and filtering capability.
We would appreciate any feedback you have on how to improve the usefulness and usability of this API.

Caveat
======
This is a preliminary work-in-progress API and may be changed 
substantially in future versions.   


See Also
========

The openblock API uses several standards for formats and protocols.  Please see the (externally maintained) documentation focused on the particular formats for more details. These include GeoJSON, Atom, and JSONP. Some helpful links:

================== ============================================================
    Format			    URL
------------------ ------------------------------------------------------------
    GeoJSON                   http://geojson.org/
------------------ ------------------------------------------------------------
     Atom                     http://www.atomenabled.org
------------------ ------------------------------------------------------------
     JSONP                    http://en.wikipedia.org/wiki/JSON#JSONP
================== ============================================================


Examples / Quickstart
=====================

FIXME 

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

Unless otherwise noted, all portions of the API using the http GET method support JSONP by 
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





GET items.json
==============

Purpose
-------
Retrieve details of a certain set of news items in GeoJSON format.

Parameters
----------
See section :ref:`search_params`


Response
--------

================== ============================================================
    Status                                Meaning
------------------ ------------------------------------------------------------
      200          The request was valid, the response contains news items 
                   that match the criteria.
------------------ ------------------------------------------------------------
      400          The request was invalid due to invalid criteria
================== ============================================================


A successful response returns a GeoJSON FeatureCollection containing a list of 
GeoJSON features.  Each resulting Feature in the collection represents a "NewsItem" 
that matches the specified search criteria ordered by item date.

NewsItem format is specified in the section :ref:`formats`


Example result

::

    FIXME example

GET items.atom
==============

Purpose
-------
Retrieve details of a certain set of news items in ATOM format.

Parameters
----------
See section :ref:`search_params`

Response
--------

================== ============================================================
    Status                                Meaning
------------------ ------------------------------------------------------------
      200          The request was valid, the response contains news items 
                   that match the criteria.
------------------ ------------------------------------------------------------
      400          The request was invalid due to invalid criteria
================== ============================================================


A successful response returns an Atom Feed.  Each resulting Atom Entry in the feed 
represents a "NewsItem" that matches the specified search criteria ordered by item date.

Format is specified in the section :ref:`formats`

Example result

::

    FIXME example

GET geocode
===========

Purpose
-------

Geocode a street address or location name to geographic location.


Parameters
----------

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
        q          address or location name to geocode 
================== ==========================================================================

Response
--------

================== ============================================================
    Status                                Meaning
------------------ ------------------------------------------------------------
      200          The request was valid and locations matching the query 
                   were found
------------------ ------------------------------------------------------------
      404          No locations matching the query were found 
------------------ ------------------------------------------------------------
      400          The request parameters were invalid
================== ============================================================


A successful response contains a GeoJSON Feature with a point corresponding to the
query given.

Example

:: 

    FIXME example


GET items/types.json 
====================

Purpose
-------

Retrieve metadata describing the types of news items available in the
system and their attributes.

Response
--------

The output maps an identifier ("slug") to a mapping of key-value pairs
describing one news item type.

Each type consists of a few strings suitable for labels in a UI
('name', 'plural_name', 'indefinite_article'), plus a 'last_updated'
date when news items of this type were last loaded.

Each news item type may also have its own extended metadata which is
described in the 'attributes' mapping.  Each attribute has a
'pretty_name' and a 'type' (one of 'text', 'bool', 'int', 'date',
'time', 'datetime').

Example

::

   [{'elvis-sightings': {
      'indefinite_article': 'an',
      'name': 'Elvis Sighting',
      'plural_name': 'Elvis Sightings',
      'slug': 'elvis-sightings',
      'last_updated': '2011-02-22',
      'attributes': {
        'verified': {
          'pretty_name': 'Verified Really Elvis',
          'type': 'bool'
       }
     }
   }]


GET locations.json
==================

Purpose
-------
Retrieve a list of predefined locations on the server as a list.

Response
--------

A list of JSON objects describing each location. Each has the
following keys:

* name - human-readable name of the location.
* slug - name suitable for use in URLs.
* area - area in square meters.
* geojson_url - link to a view of this location as GeoJSON
* description - may be blank.
* city - name of the city.

Example

::

    FIXME Example


GET locations/<locationid>.json
===============================

Purpose
-------
Retrieve detailed geometry information about a particular predefined location. 
Available location identifiers can be discovered by querying the locations.json
endpoint, see GET locations.json


Response
--------

A GeoJSON Feature object representing one named location.

Example

::

     { "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0], ...
          ]
        },
      "properties": {
        "type": "zipcode",
        "name": "02115",
        "normalized_name": "02115",
        "area": 3633354.76,
        "population": null,
        }
      },



GET locations/types.json
========================

Purpose
-------
Retrieve a list of location types, eg "towns" "zipcodes" etc which can 
be used to filter locations.

Response
--------

A JSON list describing the location types available.

Example

:: 

     FIXME [ 'towns' = { 'pretty_name': 'Town',
                   'plural_name': "Towns",
                   ...
                  }, 
        <location_type_id> = {...},
     ]




.. _search_params:

======================
Item Search Parameters
======================

Search parameters specified select all items that match all criteria simultaneously, eg specifying type="crimereport"&locationid="neighborhoods/roxbury" selects all items that are of type "crimereport" AND in the Roxbury neighborhood and no other items.

Spatial Filtering
=================

Spatial filters allow the selection of items based on geographic areas. 
At most one spatial filter may be applied per API request.


Predefined Area
---------------

Selects items in some predefined area on the server, eg a neighborhood, zipcode etc. To discover predefined areas see the endpoint "GET locations.json"

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


News Item Type 
--------------

Restricts results to a single type of news item, eg only crime reports.  The full
set of types available can be retrieved by querying the schema types list api endpoint or by inspection of the values of the 'type' field of news items returned from the api. 
See 'GET newsitems/types.json' 

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
      type         schemaid of the type to retrict results to, eg crimereport
================== ==========================================================================


Date Range
----------

Restricts results to items within a time range

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
     startdate     limits items to only those older than the given date.
                   date format is MMDDYYYY 
------------------ --------------------------------------------------------------------------
     enddate       limits items to only those newer than the given date.
                   date format is MMDDYYYY 
================== ==========================================================================



Result Limit and Skip
---------------------

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
     limit         maximum number of items to return
------------------ --------------------------------------------------------------------------
     skip          skip this number of items before returning results 
================== ==========================================================================



.. _formats:

=================
News Item Formats
=================


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


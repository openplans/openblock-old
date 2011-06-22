==================
OpenBlock REST API
==================

Introduction
============

Purpose
-------

Support simple widgets, mashups, frontends based on OpenBlock content and filtering capability.
We would appreciate any feedback you have on how to improve the usefulness and usability of this API.

Caveat
------
This is a preliminary work-in-progress API and may be changed 
substantially in future versions.   


See Also
--------

The OpenBlock API uses several standards for formats and protocols.  Please see the (externally maintained) documentation focused on the particular formats for more details. These include GeoJSON, Atom, and JSONP. Some helpful links:

================== ============================================================
    Format			    URL
------------------ ------------------------------------------------------------
    GeoJSON                   http://geojson.org/
------------------ ------------------------------------------------------------
     Atom                     http://www.atomenabled.org
------------------ ------------------------------------------------------------
.. _georss:
     GeoRSS                   http://www.georss.org/Main_Page
------------------ ------------------------------------------------------------
     JSONP                    http://en.wikipedia.org/wiki/JSON#JSONP
------------------ ------------------------------------------------------------
 rfc 3339 (date)              http://www.ietf.org/rfc/rfc3339.txt
                              (also the w3c "note-datetime" is
                              essentially the same format: http://www.w3.org/TR/NOTE-datetime)
================== ============================================================


Examples / Quickstart
---------------------

Grab some 'articles' about Roxbury

:: 

    curl "http://bos.openblock.org/api/dev1/items.json?type=articles&locationid=neighborhoods/roxbury&limit=3" > items.json


API Overview
============

URL prefix
----------

All calls to the OpenBlock API referenced in this document are prefixed by::

	/api/dev1/


Authentication and API Keys
----------------------------

Authentication for those methods which require it may currently be
accomplished in two ways:

 * HTTP Basic Auth headers

 * sending your API key in the ``X-Openblock-Key`` HTTP header

.. _apikey:

An API key may be obtained by logging in and visiting your preferences page.

Support for Cross Domain Access
-------------------------------

To enable widgets and mashups in the browser from domains other than
the host OpenBlock instance, the API supports the
`JSONP <https://secure.wikimedia.org/wikipedia/en/wiki/JSONP>`_ convention.

Unless otherwise noted, all portions of the API using the http GET method support JSONP by 
providing the "jsonp" query parameter.
The "jsonp" parameter may only contain letters, numbers, and
underscores; other characters will be removed.

GET methods supporting :ref:`Atom <atom>` output may also provide the "jsonp"
parameter. In this case the output is `JSONP-X <http://www.ajaxwith.com/JSONP-X-Output.html>`_.


Read API Endpoints
==================


GET [api prefix]
----------------

Purpose
~~~~~~~

Test the availability of this version of the API.  This request does not implement JSONP.

Response
~~~~~~~~

================== ============================================================
    Status                                Meaning
------------------ ------------------------------------------------------------
      200             This version of the API is available
------------------ ------------------------------------------------------------
      404             This version of the API is not available
================== ============================================================



GET items.json
--------------

Purpose
~~~~~~~
Retrieve details of a certain set of news items as :ref:`json`.

Parameters
~~~~~~~~~~
See section :ref:`search_params`


Response
~~~~~~~~

================== ============================================================
    Status                                Meaning
------------------ ------------------------------------------------------------
      200          The request was valid, the response contains news items 
                   that match the criteria.
------------------ ------------------------------------------------------------
      400          The request was invalid due to invalid criteria
================== ============================================================


A successful response returns a GeoJSON FeatureCollection containing a list of 
:ref:`json` features.  Each resulting Feature in the collection represents a "NewsItem" 
that matches the specified search criteria ordered by item date.

Example result

::

    {"type": "FeatureCollection", 
     "features": [
        {"type": "Feature", 
         "properties": {
            "title": "An Article About Roxbury",
            "url": "...", 
            "type": "articles",
            "description": "Test Roxbury",
            ...
         },
         "geometry": {
           "type": "Point", 
           "coordinates": [-71.086787000000001, 42.314782999999998]
         }
        }, 
     ...
    ]}

GET items.atom
--------------

Purpose
~~~~~~~
Retrieve details of a certain set of news items in ATOM format.

Parameters
~~~~~~~~~~
See section :ref:`search_params`

Response
~~~~~~~~

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

GET items/<id>.json
--------------------

Purpose
~~~~~~~

Get a single NewsItem as :ref:`json`.

Parameters
~~~~~~~~~~

None.

Response
~~~~~~~~

================== ============================================================
    Status                                Meaning
------------------ ------------------------------------------------------------
      200          Found. The body will be the NewsItem represented as
                   :ref:`json`.
------------------ ------------------------------------------------------------
      404          The NewsItem does not exist.
================== ============================================================

GET geocode
-----------

Purpose
~~~~~~~

Geocode a street address or location name to geographic location.


Parameters
~~~~~~~~~~

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
        q          address or location name to geocode 
================== ==========================================================================

Response
~~~~~~~~

================== ============================================================
    Status                                Meaning
------------------ ------------------------------------------------------------
      200          The request was valid and locations matching the query 
                   were found
------------------ ------------------------------------------------------------
      404          No locations matching the query were found.
------------------ ------------------------------------------------------------
      400          Invalid input: missing or empty 'q' parameter.
================== ============================================================


A successful response contains a GeoJSON FeatureCollection with Features corresponding to the query given.  The list will contain multiple results if
the match was ambiguous.

Example response

:: 

     "type": "FeatureCollection", 
     "features": [
      {
       "geometry": {
        "type": "Point", 
        "coordinates": [
         -71.086787000000001, 
         42.314782999999998
        ]
       }, 
       "type": "Feature", 
       "properties": {
        "city": "BOSTON", 
        "type": "neighborhoods", 
        "name": "Roxbury", 
        "query": "Roxbury"
       }
      }]}


A 404 response will return the same structure but with an empty
list of "features".


.. _get_types:

GET items/types.json 
--------------------

Purpose
~~~~~~~

Retrieve metadata describing the types of news items available in the
system and their attributes.

Response
~~~~~~~~

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


.. _get_locations:

GET locations.json
------------------

Purpose
~~~~~~~

Retrieve all predefined locations on the server as a list.

Parameters
~~~~~~~~~~

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
     type            (optional) return only locations of the specified type, eg "neighborhoods"
                     see See :ref:`get_location_types` for types.
================== ==========================================================================


Response
~~~~~~~~

A list of JSON objects describing each location. Each has the
following keys:

* name - human-readable name of the location.
* slug - name suitable for use in URLs.
* url - link to a view of this location as GeoJSON (see :ref:`get_location_detail`.
* description - may be blank.
* city - name of the city.
* type - a Location Type slug. See :ref:`get_location_types`.

Example

::

    [
     {
      "city": "YOUR CITY", 
      "description": "", 
      "url": "/api/dev1/locations/zipcodes/02108.json", 
      "type": "zipcodes", 
      "slug": "02108", 
      "name": "02108"
     }, 
     {
      "city": "YOUR CITY", 
      "description": "", 
      "url": "/api/dev1/locations/neighborhoods/allstonbrighton.json", 
      "type": "neighborhoods", 
      "slug": "allstonbrighton", 
      "name": "Allston/Brighton"
     }
    ]

.. _get_location_detail:

GET locations/<locationid>.json
--------------------------------

Purpose
~~~~~~~
Retrieve detailed geometry information about a particular predefined location. 
Available URLs can be discovered by querying the locations.json
endpoint, see :ref:`get_locations`


Response
~~~~~~~~

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
        "city": "boston",
        "name": "02115",
        "slug": "02115",
        "description": "lorem ipsum blah blah",
        "centroid": "POINT (101.0 0.5)",
        "area": 3633354.76,
        "source": "http://example.com/zip_codes_or_something",
        "population": null,
        }
      },



.. _get_location_types:

GET locations/types.json
------------------------

Purpose
~~~~~~~
Retrieve a list of location types, eg "towns", "zipcodes", etc. which can
be used to filter locations.

Response
~~~~~~~~

A JSON object describing the location types available.

Example::

     {
      "towns": {"name": "Town",
                "plural_name": "Towns",
                "scope:" "boston"},
      "zipcodes": { ... }
     }


GET places/types.json
---------------------

Purpose
~~~~~~~
Retrieve a list of place types, eg "points of interest", "police stations", etc. which can
be used to access data about places in the system.

Response
~~~~~~~~

A JSON object describing the place types available.

Example::
 
    {
        "poi": {
            "name": "Point of Interest",
            "plural_name": "Points of Interest", 
            "geojson_url": "/api/dev1/places/poi.json" 
        },
        "police": {
            "name": "Police Station",
            "plural_name": "Police Stations", 
            "geojson_url": "/api/dev1/places/police.json"
        } 
    }



GET places/<placetype>.json
---------------------------

Purpose
~~~~~~~
Retrieve a list of places of the specified type, eg "points of interest", "police stations", etc. 

Response
~~~~~~~~

A GeoJSON feature collection object describing the places of the type specified.

Example::

    {
     "type": "FeatureCollection", 
     "features": [
      {
       "geometry": {
        "type": "Point", 
        "coordinates": [
         -71.052149999999997, 
         42.332369999999997
        ]
       }, 
       "type": "Feature", 
       "properties": {
        "type": "poi", 
        "name": "Fake Monument", 
        "address": ""
       }
      }, 
      {
       "geometry": {
        "type": "Point", 
        "coordinates": [
         -71.052149999999997, 
         42.332369999999997
        ]
       }, 
       "type": "Feature", 
       "properties": {
        "type": "poi", 
        "name": "Fake Yards", 
        "address": ""
       }
      }
     ]
    }


.. _search_params:


Item Search Parameters
======================

Search parameters specified select all items that match all criteria simultaneously, eg specifying type="crimereport"&locationid="neighborhoods/roxbury" selects all items that are of type "crimereport" AND in the Roxbury neighborhood and no other items.

Spatial Filtering
-----------------

Spatial filters allow the selection of items based on geographic areas. 
At most one spatial filter may be applied per API request.


Predefined Area
~~~~~~~~~~~~~~~

Selects items in some predefined area on the server, eg a neighborhood, zipcode etc. To discover predefined areas see the endpoint "GET locations.json"

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
   locationid      server provided identifier for predefined location.
                   eg: "neighborhoods/roxbury"
================== ==========================================================================


Bounding Circle
~~~~~~~~~~~~~~~

Selects items within some distance of a given point.

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
      center	    <lon>,<lat> comma separated list of 2 floating point 
                    values representing the longitude and latitude of the 
                    center of the circle. eg: center=-71.191153,42.227865

------------------ --------------------------------------------------------------------------
      radius	   positive floating point maximum distance in meters from the specified 
                   center point
================== ==========================================================================


Other Filters
-------------


News Item Type 
~~~~~~~~~~~~~~

Restricts results to a single type of news item, eg only crime reports.  The full
set of types available can be retrieved by querying the schema types list api endpoint or by inspection of the values of the 'type' field of news items returned from the api. 
See 'GET newsitems/types.json' 

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
      type         schemaid of the type to retrict results to, eg crimereport
================== ==========================================================================


Date Range
~~~~~~~~~~

Restricts results to items within a time range


================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
     startdate     limits items to only those newer than the given date.
                   date format is YYYY-MM-DD or rfc3339 for date/time
------------------ --------------------------------------------------------------------------
     enddate       limits items to only those older than the given date.
                   date format is YYYY-MM-DD or rfc3339 for date/time
================== ==========================================================================


Result Limit and Offset
~~~~~~~~~~~~~~~~~~~~~~~

================== ==========================================================================
    Parameter                                Description
------------------ --------------------------------------------------------------------------
     limit         maximum number of items to return. default is 25, max 200
------------------ --------------------------------------------------------------------------
     offset        skip this number of items before returning results. default is 0 
================== ==========================================================================


Write API Endpoints
===================

.. _post_items:

POST items/
-----------

Purpose
~~~~~~~

Create a new NewsItem.  :ref:`Authentication required <auth>`.


Parameters
~~~~~~~~~~

The body of the POST must be a :ref:`json` representation of
a single NewsItem.

Note that you must include either the ``geometry``, or
``properties['location_name']``, or both:

* If ``geometry`` is omitted, the location_name will be used for
  geocoding to generate a geometry.
* If ``location_name`` is omitted, the geometry will be used for
  reverse-geocoding to generate a block name.
* If both are omitted, or geocoding/reverse-geocoding fails, it is an
  error.


Response
~~~~~~~~

================== ============================================================
    Status                                Meaning
------------------ ------------------------------------------------------------
      201          Created the NewsItem successfully. The
                   'Location' header will be a URI to the JSON
                   representation of this NewsItem.
------------------ ------------------------------------------------------------
      400          Invalid input.  In future versions of the API this
                   should contain validation hints, format to be determined.
------------------ ------------------------------------------------------------
      401          Permission denied.
================== ============================================================




.. _formats:


News Item Formats
=================

.. _json:

NewsItem JSON Format
--------------------

A NewsItem is represented by a GeoJSON Feature containing:
 * a "geometry" attribute representing its specific location, generally a Point.
 * a "properties" attribute containing details of the news item according to its schema.
 * a "type" attribute, which is always "Feature".

See the GeoJSON specification for additional information on GeoJSON: 
http://geojson.org/geojson-spec.html

Common Properties
~~~~~~~~~~~~~~~~~

The following properties are common to all Schema and will always be
present:

============= ================== ==========================================
Name          Type               Meaning
------------- ------------------ ------------------------------------------
title         text               Headline or other title from the source.
------------- ------------------ ------------------------------------------
description   text               Summary of the news item.
------------- ------------------ ------------------------------------------
url           text               Original URL where the news was found.
------------- ------------------ ------------------------------------------
pub_date      rfc3339 date/time  Date/time this Item was added to the
                                 OpenBlock site. (Set automatically in
                                 :ref:`post_items`.)
------------- ------------------ ------------------------------------------
item_date     rfc3339 date       Date this news occurred, or was
                                 published on the original source site.
------------- ------------------ ------------------------------------------
location_name text               Human-readable name of the location.
============= ================== ==========================================


Extended Properties: Schema Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additional properties may be returned according to the NewsItem's
type, aka :ref:`schema <newsitem-schemas>`.

In order to know what attributes are defined for each schema, or to
know what to include in :ref:`post_items`, you can do a request
to :ref:`get_types`.

NewsItem Schema attributes are output in the corresponding JSON value
type if one exists, otherwise a formatted string is used.

================== ==========================================================================
    Field Type                  JSON Representation
------------------ --------------------------------------------------------------------------
      string        string
------------------ --------------------------------------------------------------------------
      number        number
------------------ --------------------------------------------------------------------------
      boolean       boolean
------------------ --------------------------------------------------------------------------
      datetime      rfc3339 formatted datetime string, eg: "1999-12-29T12:11:45Z"
------------------ --------------------------------------------------------------------------
      date          rfc3339 formatted date string, eg: "1999-12-29"
------------------ --------------------------------------------------------------------------
      time          rfc3339 formatted time string, eg: "12:11:45Z" 
================== ==========================================================================


.. _atom:

NewsItem Atom Format
--------------------

Generally follows the :ref:`Atom <atom>` specification.
Location information is specified with :ref:`GeoRSS-Simple <georss>`.

Extended schema attributes are specified in the
"http://openblock.org/ns/0" namespace.

FIXME: more detail, example


#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#


from ebpub.db.models import Location, LocationSynonym
from ebpub.geocoder import SmartGeocoder, AmbiguousResult, InvalidBlockButValidStreet
from ebpub.streets.models import Place, PlaceSynonym
from django.conf import settings
import logging

logger = logging.getLogger('ebpub.streets.utils')

def full_geocode(query, search_places=True):
    """
    Tries the full geocoding stack on the given query (a string):
        * Normalizes whitespace/capitalization
        * Searches the Misspelling table to corrects location misspellings
        * Searches the Location table
        * Failing that, searches the Place table (if search_places is True)
        * Failing that, uses the given geocoder to parse this as an address
        * Failing that, raises whichever error is raised by the geocoder --
          except AmbiguousResult, in which case all possible results are
          returned

    Returns a dictionary of {type, result, ambiguous}, where ambiguous is True
    or False and type can be:
        * 'location' -- in which case result is a Location object.
        * 'place' -- in which case result is a Place object. (This is only
          possible if search_places is True.)
        * 'address' -- in which case result is an Address object as returned
          by geocoder.geocode().
        * 'block' -- in which case result is a list of Block objects.

    If ambiguous is True, result will be a list of objects.
    """
    # Search the Location table.
    try:
        canonical_loc = LocationSynonym.objects.get_canonical(query)
        loc = Location.objects.get(normalized_name=canonical_loc)
    except Location.DoesNotExist:
        pass
    else:
        logger.debug('geocoded %r to Location %s' % (query, loc))
        return {'type': 'location', 'result': loc, 'ambiguous': False}

    # Search the Place table, for stuff like "Sears Tower".
    if search_places:
        canonical_place = PlaceSynonym.objects.get_canonical(query)
        places = Place.objects.filter(normalized_name=canonical_place)
        if len(places) == 1:
            logger.debug(u'geocoded %r to Place %s' % (query, places[0]))

            return {'type': 'place', 'result': places[0], 'ambiguous': False}
        elif len(places) > 1:
            logger.debug(u'geocoded %r to multiple Places: %s' % (query, unicode(places)))
            return {'type': 'place', 'result': places, 'ambiguous': True}

    # Try geocoding this as an address.
    geocoder = SmartGeocoder(use_cache=getattr(settings, 'EBPUB_CACHE_GEOCODER', False))
    try:
        result = geocoder.geocode(query)
    except AmbiguousResult, e:
        logger.debug('Multiple addresses for %r' % query)
        return {'type': 'address', 'result': e.choices, 'ambiguous': True}
    except InvalidBlockButValidStreet, e:
        logger.debug('Invalid block for %r, returning all possible blocks' % query)
        return {'type': 'block', 'result': e.block_list, 'ambiguous': True, 'street_name': e.street_name, 'block_number': e.block_number}
    except:
        raise
    logger.debug('SmartGeocoder for %r returned %s' % (query, result))
    return {'type': 'address', 'result': result, 'ambiguous': False}

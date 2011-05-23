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

import logging
import re
import string
from itertools import izip

# The following are all relative imports
from suffixes import suffixes
from states import states
from cities import cities
from numbered_streets import numbered_streets

logger = logging.getLogger('ebpub.geocoder.parser')

class ParsingError(Exception):
    pass

#################
# STANDARDIZERS #
#################

DIRECTIONALS = {
    'N': 'NORTH',
    'NE': 'NORTHEAST',
    'E': 'EAST',
    'SE': 'SOUTHEAST',
    'S': 'SOUTH',
    'SW': 'SOUTHWEST',
    'W': 'WEST',
    'NW': 'NORTHWEST',
}

class Standardizer(object):
    """Replaces a suffix, directional, state, etc. with the preferred standard form.

    For example, given the text "avenu" for suffixes, returns "AVE".

    >>> suff_standardizer = Standardizer(suffixes)
    >>> suff_standardizer("avenu")
    'AVE'
    >>> dir_standardizer = Standardizer(DIRECTIONALS)
    >>> dir_standardizer("north")
    'N'
    >>> dir_standardizer("n")
    'N'
    """
    def __init__(self, d):
        self.replacement = {}
        for standard, options in d.items():
            standard = standard.upper()
            if isinstance(options, basestring):
                options = [options]
            for opt in options:
                self.replacement[opt.upper()] = standard
            # Also map the standard to itself.
            self.replacement[standard] = standard

    def __call__(self, s):
        if s.upper() in self.replacement:
            return self.replacement[s.upper()]
        else:
            return s

def number_standardizer(s):
    """
    Removes the second number in hyphenated addresses such as '123-02', as
    used in NYC. Note that this also removes the second number in address
    ranges.

    >>> number_standardizer('1-2')
    '1'
    >>> number_standardizer('100-200')
    '100'
    >>> number_standardizer('12A-12B')
    '12'
    >>> number_standardizer('x')
    'x'
    """
    m = re.search(r'^(\d+)[A-Z]?(?:-\d+[A-Z]?)?$', s)
    if not m:
        # We shouldn't reach this, but if the regex doesn't match, just return the input.
        return s
    return m.group(1)

dir_standardizer = Standardizer(DIRECTIONALS)

STANDARDIZERS = {
    'number': number_standardizer,
    'pre_dir': dir_standardizer,
    'street': Standardizer(numbered_streets),
    'suffix': Standardizer(suffixes),
    'post_dir': dir_standardizer,
    'city': Standardizer(cities),
    'state': Standardizer(states),
}

# Regex which matches all punctuation, except for dashes (which
# might be used in NYC addresses) and ampersands.
preserved_puncts = "-&"
punct = re.compile(r'[%s]' % re.escape("".join(set(string.punctuation) - set(preserved_puncts))))

half_addresses_re = re.compile(r'(?<=\s)[I1]/2(?=\s)')
multi_dash_re = re.compile(r'(?<=\d)\s*-+\s*(?=\d)')
zip_plus_4_re = re.compile(r'(?<=^\d{5})-\d{4}$')

def normalize(location):
    """
    Normalizes an address string for parsing, comparisons.

    >>> normalize(u"1972 n. dawson ave. chicago il")
    u'1972 N DAWSON AVE CHICAGO IL'
    >>> normalize(u"1972 n. dawson ave., chicago il")
    u'1972 N DAWSON AVE CHICAGO IL'
    >>> normalize(u"n kimball ave & w diversey ave")
    u'N KIMBALL AVE & W DIVERSEY AVE'
    """
    old_location = location
    location = location.upper()
    location = half_addresses_re.sub('', location) # Strip "1/2" addresses.
    location = multi_dash_re.sub('-', location)
    location = punct.sub('', location) # Remove all punctuation except dashes, and ampersands.
    location = re.sub(r'\s+', ' ', location.strip()) # Strip/normalize whitespace.
    location = zip_plus_4_re.sub('', location) # Strip the +4 part of a ZIP+4.
    logger.debug("normalized: %r to %r" % (old_location, location))
    return location

def strip_unit(location):
    """
    Given an address string, strips the apartment number, suite number, etc.

    >>> strip_unit('200 E 31st st')
    '200 E 31st st'
    >>> strip_unit('200 E 31st st unit 123')
    '200 E 31st st'
    >>> strip_unit('123 W broadway apt B')
    '123 W broadway'
    >>> strip_unit('99 s northshore drive apt. B')
    '99 s northshore drive'
    >>> strip_unit('45 carlton ave #12')
    '45 carlton ave'
    >>> strip_unit('148 lafayette st suite 13')
    '148 lafayette st'

    """
    return re.sub(r'(?i)(\s*,)?\s*(?:space\s+|suite\s+|ste\.?\s+|unit:?\s+|apt\.?\s+|\#\s*)[-\#0-9a-z]*$', '', location)

###########
# PARSING #
###########

def abbrev_regex(d, case_insensitive=True, matches_entirely=True):
    """
    Returns a regular expression pattern that matches an abbreviation.

    >>> suffixes = {
    ...     'av': ['ave', 'avenue'],
    ...     'st': ['str', 'street'],
    ...     'rd': 'road'
    ... }
    >>> regex = abbrev_regex(suffixes)
    >>> re.search(regex, "Ave")  # doctest: +ELLIPSIS
    <_sre.SRE_Match object at ...>
    >>> re.search(regex, " Ave ") == None
    True
    >>> regex = abbrev_regex(suffixes, case_insensitive=False)
    >>> re.search(regex, "str")  # doctest: +ELLIPSIS
    <_sre.SRE_Match object at ...>
    >>> re.search(regex, "Str") == None
    True
    >>> regex = abbrev_regex(suffixes, matches_entirely=False)
    >>> re.search(regex, " Road ")  # doctest: +ELLIPSIS
    <_sre.SRE_Match object at ...>
    """
    alts = []
    for k, v in d.items():
        if isinstance(v, basestring):
            v = [v]
        alts.append(k)
        alts.extend(v)
    pattern = r"(?:%s)" % "|".join(alts)
    if matches_entirely:
        pattern = "^" + pattern + "$"
    if case_insensitive:
        pattern = "(?i)" + pattern
    return pattern

directional_re = re.compile(abbrev_regex(DIRECTIONALS))

TOKEN_REGEXES = {
    'number': re.compile(r'^\d+[A-Z]?(?:-\d+[A-Z]?)?$'),
    'pre_dir': directional_re,
    'street': re.compile(r'^[0-9]{1,3}(?:ST|ND|RD|TH)|[A-Z]{1,25}|[0-9]{1,3}$'),
    'suffix': re.compile(abbrev_regex(suffixes)),
    'post_dir': directional_re,

    # Cities are assumed to have at least three letters and at most 25 letters.
    # This is a safe assumption that comes from this page:
    # http://www.geographylists.com/list17f.html
    'city': re.compile(r'^[A-Z]{3,25}$'),

    # State words can have between 2 and 13 letters ('MASSACHUSETTS' is the
    # longest, with 13 letters). Note that this doesn't count states whose
    # names take up more than one word. This regex matches *single* words.
    'state': re.compile(r'^[A-Z]{2,13}$'),

    'zip': re.compile(r'^\d{5}(?:-\d{4})?$'),
}

class Location(dict):
    location_keys = ('number', 'pre_dir', 'street', 'suffix', 'post_dir', 'city', 'state', 'zip')

    def __init__(self, *args):
        super(Location, self).__init__(*args)
        for location_key in self.location_keys:
            if location_key not in self:
                self[location_key] = None

    def __repr__(self):
        return "{%s}" % ", ".join(["%r: %r" % (k, self[k]) for k in self.location_keys])

    def __setitem__(self, name, value):
        if name not in self.location_keys:
            raise AttributeError(repr(name))
        super(Location, self).__setitem__(name, value)

def address_combinations():
    """
    Generator that yields a list for every possible combination of address
    tokens. For example:
        ['number', 'pre_dir', 'street']
        ['number', 'street', 'city', 'state']
    """
    # There are about 2000 combinations at last count.
    for number_times in (0, 1):
        for pre_dir_times in (0, 1):
            for street_times in (1, 2, 3, 4, 5):
                for suffix_times in (0, 1):
                    for post_dir_times in (0, 1):
                        for city_times in (0, 1, 2, 3, 4):
                            # If a city isn't given, then a state isn't allowed.
                            for state_times in (city_times == 0 and (0,) or (0, 1, 2)):
                                for zip_times in (0, 1):
                                    yield ['number'] * number_times + ['pre_dir'] * pre_dir_times + ['street'] * street_times + ['suffix'] * suffix_times + ['post_dir'] * post_dir_times + ['city'] * city_times + ['state'] * state_times + ['zip'] * zip_times


punc_split = re.compile(r"\S+").findall

def parse(location):
    s = strip_unit(normalize(location))
    logger.debug('parse: normalized and stripped %r to %r' % (location, s))
    tokens = punc_split(s)
    len_tokens = len(tokens)
    result_list = []

    for token_types in address_combinations():
        if len(token_types) == len_tokens:
            try:
                for token, token_type in izip(tokens, token_types):
                    if not TOKEN_REGEXES[token_type].match(token):
                        raise StopIteration() # Token regex didn't match.
            except StopIteration:
                continue

            # If we made it this far, then all of the tokens are valid.
            # Create the Location object.
            result = Location()
            for token, token_type in izip(tokens, token_types):
                if result[token_type]:
                    result[token_type] += ' ' + token
                else:
                    result[token_type] = token

            # Standardize all values.
            for key, value in result.items():
                if value and key in STANDARDIZERS:
                    result[key] = STANDARDIZERS[key](value)
                    logger.debug('parse: standardized %r to %r' % (value, result[key]))

            logger.debug('parse: %r gave possible result address %s' % (s, result))
            result_list.append(result)

    if not result_list:
        raise ParsingError("Failed to parse location %r" % location)
    return result_list

if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)

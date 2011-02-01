#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebgeo
#
#   ebgeo is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebgeo is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebgeo.  If not, see <http://www.gnu.org/licenses/>.
#

PAIR_SEP = "|"
KEY_VALUE_SEP = ":"

def encode_theme_data(data):
    """
    Encodes a dictionary suitable for passing theme data in a URI to the
    map server.

    Assumes URI encoding will be handled upstream.

    >>> d = {"logan-square": 54, "edgewater": 31, "the-loop": 44}
    >>> s = encode_theme_data(d)
    >>> s == 'the-loop:44|logan-square:54|edgewater:31'
    True
    """
    return PAIR_SEP.join(["%s%s%s" % (k, KEY_VALUE_SEP, v) for k, v in data.items()])

def decode_theme_data(s):
    """
    Decodes a string that's been encoding by encode_theme_data() and
    returns a dictionary.

    Assumes already URI-decoded.

    >>> d = decode_theme_data("the-loop:44|logan-square:54|edgewater:31")
    >>> d == {"logan-square": 54, "edgewater": 31, "the-loop": 44}
    True
    """
    pairs = [s.split(KEY_VALUE_SEP) for s in s.split(PAIR_SEP)]
    return dict([(k, float(v)) for k, v in pairs])


if __name__ == "__main__":
    import doctest
    doctest.testmod()

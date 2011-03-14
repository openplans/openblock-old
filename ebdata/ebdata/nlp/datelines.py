#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

import re

dateline_re = re.compile(ur"""
    (?:
        (?:                                                     # Either a newline, or a
            ^                                                   # <p> / <div>, followed by tags/space
            |
            </?\s*(?:[Pp]|[Dd][Ii][Vv])[^>]*>
        )
        (?:<[^>]*>|\s)*                                         # The start of a line
    )
    (?:\(\d\d?-\d\d?\)\s+\d\d?:\d\d\s+[PMCE][SD]T\s+)?          # Optional timestamp -- e.g., "(07-17) 13:09 PDT"
    ([A-Z][A-Z.]*[A-Z.,](?:\s*[A-Z][A-Za-z.]*[A-Za-z.,]){0,4})  # The dateline itself
    (?:                                                         # Optional parenthetical news outlet
        \s+
        \(
            [-A-Za-z0-9]{1,15}
            (?:\s+[-A-Za-z0-9]{1,15}){0,4}
        \)
    )?
    \s*                                                         # Optional space before dash
    (?:\xa0--\xa0|--|\x97|\u2014|\u2015|&\#8213;|&\#151;|&\#x97;)     # Dash (or emdash)
    """, re.MULTILINE | re.VERBOSE)

# That dash/emdash regex bears some explaining as i'm guessing it was added to piecemeal:
#
# \xa0 =  non-breaking space in cp1252
# \x97 = em dash in cp1252
# \u2014 = em dash in unicode (assuming we've already decoded)
# \u2015 = 'horizontal bar' in unicode (assuming we've already decoded)
# &#8213; = 'horizontal bar' as HTML char ref, numeric
# &#x2015; = 'horizontal bar' as HTML char ref, hex
# &#151; = em dash as HTML char ref, numeric
# &#x97; = em dash as HTML char ref, hex

def guess_datelines(text):
    """
    Given some text (with or without HTML), returns a list of the dateline(s)
    in it. Returns an empty list if none are found.
    """
    return dateline_re.findall(text)

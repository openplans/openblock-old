#   Copyright 2012 OpenPlans and contributors
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

"""
US street address prefix standardization,
derived from http://pe.usps.gov/text/pub28/28apf.html
"""

prefixes = {
    'COUNTY HIGHWAY': ['COUNTY HIGHWAY', 'COUNTY HWY', 'CNTY HWY'],
    'COUNTY ROAD': ['COUNTY RD', 'COUNTY ROAD', 'CR', 'CNTY RD'],
    'EXPRESSWAY': ['EXPRESSWAY', 'EXPWY'],
    'FM': ['FARM TO MARKET', 'FM', 'HWY FM'],
    'HIGHWAY': ['HIGHWAY', 'HIWAY', 'HWY'],
    'INTERSTATE': ['I', 'INTERSTATE', 'IH', 'INTERSTATE HWY'],
    'LOOP': ['LOOP'],
    'ROAD': ['RD', 'ROAD'],
    'ROUTE': ['RT', 'RTE', 'ROUTE'],
    'RANCH ROAD': ['RANCH RD'],
    'STATE HIGHWAY': ['ST HIGHWAY', 'STATE HWY', 'ST HWY'],
    # Problem: 'SR' is ambiguous, could be STATE ROAD or STATE ROUTE.
    # We choose STATE ROUTE.
    'STATE ROAD': ['ST RD', 'STATE ROAD',], # 'SR'],
    'STATE ROUTE': ['SR', 'ST RT', 'STATE ROUTE', 'STATE RTE'],
    'TOWNSHIP ROAD': ['TOWNSHIP RD', 'TSR', 'TOWNSHIP ROAD'],
    'US HIGHWAY': ['US', 'US HIGHWAY', 'US HWY'],

}

state_prefixes = {}
from states import states
for abbr, full in states.items():
    # Example:
    #'KY HIGHWAY': ['KENTUCKY', 'KY HIGHWAY', 'KENTUCKY HIGHWAY', 'KY', 'KY HWY'],
    key = abbr + ' HIGHWAY'
    vals = [key, abbr, full, full + ' HIGHWAY', abbr + ' HWY']
    state_prefixes[key] = vals

    # Example:
    #'KY STATE HIGHWAY': ['KY ST HWY', 'KY STATE HIGHWAY', 'KENTUCKY STATE HIGHWAY'],
    key = abbr + ' STATE HIGHWAY'
    vals = [key, abbr + ' ST HWY', full + ' STATE HIGHWAY']
    state_prefixes[key] = vals

    # Example:
    #'CA COUNTY ROAD': ['CA COUNTY RD', 'CALIFORNIA COUNTY ROAD', 'CA COUNTY ROAD'],
    key = abbr + ' COUNTY ROAD'
    vals = [key, abbr + ' COUNTY RD', full + ' COUNTY ROAD']


prefixes.update(state_prefixes)

# These examples were in the file but aren't separate prefixes.
# 'INTERSTATE 55 BYP': 'I 55 BYPASS',
# 'INTERSTATE 26 BYPASS RD': 'I 26 BYP ROAD',
# 'INTERSTATE 44 FRONTAGE RD': 'I 44 FRONTAGE ROAD',
# 'HIGHWAY 11 BYP': 'HWY 11 BYPASS',
# 'HIGHWAY 66 FRONTAGE RD': 'HWY 66 FRONTAGE ROAD',
# 'HIGHWAY 3 BYPASS RD': 'HIGHWAY 3 BYP ROAD',



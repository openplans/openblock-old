#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#
# -*- coding: utf-8 -*-

from background_task import background
from urllib import urlretrieve
from string import maketrans
from zipfile import ZipFile
from ebpub.db.bin.import_zips import parse_args, ZipImporter
import tempfile
import os

# These may look suspiciously like numbers, but we're matching identifiers
# by the Census, and who knows what they'll do. Extracted from the source of
# http://www2.census.gov/cgi-bin/shapefiles2009/national-files
CENSUS_STATES = (
    ("01", "Alabama"),
    ("02", "Alaska"),
    ("60", "American Samoa"),
    ("04", "Arizona"),
    ("05", "Arkansas"),
    ("06", "California"),
    ("08", "Colorado"),
    ("69", "Commonwealth of the Northern Mariana Islands"),
    ("09", "Connecticut"),
    ("10", "Delaware"),
    ("11", "District of Columbia"),
    ("12", "Florida"),
    ("13", "Georgia"),
    ("66", "Guam"),
    ("15", "Hawaii"),
    ("16", "Idaho"),
    ("17", "Illinois"),
    ("18", "Indiana"),
    ("19", "Iowa"),
    ("20", "Kansas"),
    ("21", "Kentucky"),
    ("22", "Louisiana"),
    ("23", "Maine"),
    ("24", "Maryland"),
    ("25", "Massachusetts"),
    ("26", "Michigan"),
    ("27", "Minnesota"),
    ("28", "Mississippi"),
    ("29", "Missouri"),
    ("30", "Montana"),
    ("31", "Nebraska"),
    ("32", "Nevada"),
    ("33", "New Hampshire"),
    ("34", "New Jersey"),
    ("35", "New Mexico"),
    ("36", "New York"),
    ("37", "North Carolina"),
    ("38", "North Dakota"),
    ("39", "Ohio"),
    ("40", "Oklahoma"),
    ("41", "Oregon"),
    ("42", "Pennsylvania"),
    ("72", "Puerto Rico"),
    ("44", "Rhode Island"),
    ("45", "South Carolina"),
    ("46", "South Dakota"),
    ("47", "Tennessee"),
    ("48", "Texas"),
    ("49", "Utah"),
    ("50", "Vermont"),
    ("78", "Virgin Islands of the United States"),
    ("51", "Virginia"),
    ("53", "Washington"),
    ("54", "West Virginia"),
    ("55", "Wisconsin"),
    ("56", "Wyoming"),
)

@background
def download_state_shapefile(state, zipcodes):
    n = dict(CENSUS_STATES)[state].upper().translate(maketrans(' ', '_'))
    url = "http://tigerline.census.gov/geo/tiger/TIGER2009/%(id)s_%(name)s/tl_2009_%(id)s_zcta5.zip" % { 'id': state, 'name': n }
    # TODO: handle network errors, etc
    # TODO: cache downloads?
    filename, headers = urlretrieve(url)
    tmp = tempfile.gettempdir()  # usually /tmp, but respects $TMPDIR
    name = 'tl_2009_%s_zcta5' % state
    files = [name + ext for ext in ('.shp', '.dbf', '.prj', '.shp.xml', '.shx')]
    shapefile = os.path.join(tmp, '%s.shp' % name)
    # TODO: handle errors (permission, tmp doesn't exist, zipfile corrupt,
    # expected files aren't in the archive ...)
    ZipFile(filename, 'r').extractall(tmp, files)
    for zipcode in zipcodes:
        import_zip_from_shapefile(shapefile, zipcode)

#@background
def import_zip_from_shapefile(filename, zipcode):
    # Location importing is unfortunately tightly coupled to option parsing,
    # so this zip importer creates a fake option block to call it with rather
    # than risk a big restructuring.
    opts, args = parse_args()
    importer = ZipImporter(filename, opts)
    try:
        importer.import_zip(zipcode)
    except KeyError:
        next # zip file not in shapefile. TODO: report error somehow

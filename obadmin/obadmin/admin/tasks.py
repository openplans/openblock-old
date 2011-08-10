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
from django.conf import settings
from ebdata.retrieval.retrievers import Retriever
from string import maketrans
from zipfile import ZipFile
from ebpub.db.bin.import_locations import layer_from_shapefile
from ebpub.db.bin.import_zips import ZipImporter
from ebpub.utils.logutils import log_exception
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
    name         = "tl_2009_%s_zcta5" % state
    zip_filename = "%s.zip" % name
    cache_dir    = getattr(settings, 'HTTP_CACHE', tempfile.gettempdir())
    path         = os.path.join(cache_dir, zip_filename)
    url = "http://tigerline.census.gov/geo/tiger/TIGER2009/%(id)s_%(name)s/%(zip_filename)s" % { 'id': state, 'name': n, 'zip_filename': zip_filename }

    Retriever().cached_get_to_file(url, path)

    files = [name + ext for ext in ('.shp', '.dbf', '.prj', '.shp.xml', '.shx')]
    shapefile = os.path.join(cache_dir, '%s.shp' % name)
    # TODO: handle corrupt/incomplete/missing files zipfile
    # expected files aren't in the archive ...)
    try:
        ZipFile(path, 'r').extractall(cache_dir, files)
    except:
        log_exception()
        return
    for zipcode in zipcodes:
        import_zip_from_shapefile(shapefile, zipcode)

@background
def import_zip_from_shapefile(filename, zipcode):
    layer = layer_from_shapefile(filename, 0)
    importer = ZipImporter(layer, 'ZCTA5CE')
    try:
        importer.import_zip(zipcode)
    except:
        log_exception()
        return

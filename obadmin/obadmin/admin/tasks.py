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
from tempfile import mkdtemp
from zipfile import ZipFile
from ebpub.db.bin.import_locations import layer_from_shapefile
from ebpub.db.bin.import_zips import ZipImporter
from ebpub.streets.blockimport.tiger.import_blocks import TigerImporter
from ebpub.streets.bin import populate_streets
from ebpub.utils.logutils import log_exception
import glob
import os
import shutil
import tempfile

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
    print "Starting download"
    n = dict(CENSUS_STATES)[state].upper().replace(' ', '_')
    name         = "tl_2009_%s_zcta5" % state
    zip_filename = "%s.zip" % name
    cache_dir    = getattr(settings, 'HTTP_CACHE', tempfile.gettempdir())
    path         = os.path.join(cache_dir, zip_filename)
    url = "http://tigerline.census.gov/geo/tiger/TIGER2009/%(id)s_%(name)s/%(zip_filename)s" % { 'id': state, 'name': n, 'zip_filename': zip_filename }

    Retriever().cached_get_to_file(url, path)
    print "fetched %s" % url
    files = [name + ext for ext in ('.shp', '.dbf', '.prj', '.shp.xml', '.shx')]
    shapefile = os.path.join(cache_dir, '%s.shp' % name)
    # TODO: handle corrupt/incomplete/missing files zipfile
    # expected files aren't in the archive ...)
    try:
        ZipFile(path, 'r').extractall(cache_dir, files)
        print "extracted"
    except:
        log_exception()
        return
    for zipcode in zipcodes:
        print "importing %s" % zipcode
        import_zip_from_shapefile(shapefile, zipcode)
        print "... ok"
    print "All zip codes done"

@background
def import_zip_from_shapefile(filename, zipcode):
    layer = layer_from_shapefile(filename, 0)
    importer = ZipImporter(layer, 'ZCTA5CE')
    try:
        importer.import_zip(zipcode)
    except:
        log_exception()
        return

@background
def import_blocks_from_shapefiles(edges, featnames, faces, place, city=None,
                                  fix_cities=False, regenerate_intersections=True):
    # File args are paths to zip files.

    outdir = mkdtemp(suffix='-block-shapefiles')
    try:
        for path in (edges, featnames, faces, place):
            ZipFile(path, 'r').extractall(outdir)
    except:
        # TODO: display error in UI
        log_exception()
        shutil.rmtree(outdir)
        raise
    finally:
        os.unlink(edges)
        os.unlink(featnames)
        os.unlink(faces)
        os.unlink(place)
    try:
        edges = glob.glob(os.path.join(outdir, '*edges.shp'))[0]
        featnames = glob.glob(os.path.join(outdir, '*featnames.dbf'))[0]
        faces = glob.glob(os.path.join(outdir, '*faces.dbf'))[0]
        place = glob.glob(os.path.join(outdir, '*place.shp'))[0]
        tiger = TigerImporter(
            edges,
            featnames,
            faces,
            place,
            filter_city=city,
            fix_cities=fix_cities,
            )
        num_created = tiger.save()
    finally:
        shutil.rmtree(outdir)
    if regenerate_intersections:
        populate_streets_task()
    return num_created

@background
def populate_streets_task():
    populate_streets.populate_streets()
    populate_block_intersections()

@background
def populate_block_intersections():
    populate_streets.populate_block_intersections()
    populate_intersections()

@background
def populate_intersections():
    populate_streets.populate_intersections()

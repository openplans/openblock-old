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


from django.core.management.base import BaseCommand
from ebpub.utils.script_utils import die, makedirs, wget, unzip
import os

class Command(BaseCommand):
    help = 'Import Boston neighborhoods as ebpub.db.Locations.'

    def handle(self, *args, **options):
        HERE = os.getcwd()
        print "Working directory is", HERE



        HOOD_SERVER="http://developer.openblockproject.org/raw-attachment/ticket/62"
        HOOD_FILE="Planning_districts_revised.zip" 
        HOOD_URL="%s/%s" % (HOOD_SERVER, HOOD_FILE)
        HOOD_FOLDER = os.path.join(HERE, 'neighborhood_data')

        print "Downloading neighborhood data..."
        makedirs(HOOD_FOLDER) or die("couldn't create %s" % HOOD_FOLDER)
        wget(HOOD_URL, cwd=HOOD_FOLDER) or die("Could not download %s" % HOOD_URL)
        hood_path = os.path.join(HOOD_FOLDER, HOOD_FILE)
        unzip(hood_path, cwd=HOOD_FOLDER) or die("Could not unzip %s" % hood_path)

        print "Importing neighborhoods..."
        from ebpub.db.bin import import_hoods
        import_hoods.main(['-v', '-n', 'PD', HOOD_FOLDER])
        print "Done."

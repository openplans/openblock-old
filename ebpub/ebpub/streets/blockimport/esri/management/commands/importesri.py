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

from django.core.management.base import BaseCommand, CommandError
from ebpub.streets.blockimport.esri import importers

class Command(BaseCommand):
    help = 'Import a shapefile from the ESRI data'
    
    def handle(self, *args, **options):
        if len(args) != 3:
            raise CommandError('Usage: import_esri <importer_type> <city> </path/to/shapefile/>')
        (importer_type, city, shapefile) = args
        importer_mod = getattr(importers, importer_type, None) 
        if importer_mod is None:
            raise CommandError('Invalid importer_type %s' % importer_type)
        importer_cls = getattr(importer_mod, 'EsriImporter', None)
        if importer_cls is None:
            raise CommandError('importer module must define an EsriImporter class')
        importer = importer_cls(shapefile, city)
        if options['verbosity'] == 2:
            verbose = True
        else:
            verbose = False
        num_created = importer.save(verbose)
        if options['verbosity'] > 0:
            print 'Created %d %s(s)' % (num_created, importer_type)

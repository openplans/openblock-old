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
    help = 'Import Boston local news as ebpub.db.NewsItems.'

    def handle(self, *args, **options):
        HERE = os.getcwd()
        print "Working directory is", HERE

        print "Adding latest news..."
        from ebdata.scrapers.general.georss.retrieval import main as news_main
        news_main(["http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&subject=massachusetts&scope=bonzai"])
        # more feeds from Joel. Local blog news:
        news_main(["http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&scope=blogs&count=250&subject=massachusetts&format=atom"])

        print "Adding latest events..."
        from ebdata.scrapers.us.ma.boston.events.retrieval import main as events_main
        events_main()

        print "Adding police reports..."
        from ebdata.scrapers.us.ma.boston.police_reports.retrieval import main as pr_main
        pr_main()

        print " Adding building permits..."
        from ebdata.scrapers.us.ma.boston.building_permits.retrieval import PermitScraper
        PermitScraper().update()


        print "Adding GeoReport issues..."
        from ebdata.scrapers.general.open311.georeportv2 import main as georeport_main
        georeport_main(['--html-url-template=http://seeclickfix.com/open311/v2/requests/%s.html',
                        'http://seeclicktest.com/open311/v2'])


        # TODO: fix traceback:  ebdata.blobs.scrapers.NoSeedYet: You need to add a Seed with the URL 'http://www.cityofboston.gov/news/
        #echo Adding press releases...
        #python everyblock/everyblock/cities/boston/city_press_releases/retrieval.py || die


        print "Updating aggregates, see ebpub/README.txt..."
        from ebpub.db.bin.update_aggregates import update_all_aggregates
        update_all_aggregates(verbose=True)

        print """
___________________________________________________________________

 *** NOT adding restaurant inspections, it may take hours. ***

  If you want to load them, do:
  django-admin.py import_boston_restaurants
___________________________________________________________________
"""

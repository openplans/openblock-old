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

"""
Sample config file for the updaterdaemon.

"""

import os
from ebdata.retrieval.updaterdaemon.config import multiple_hourly, multiple_daily

def do_seeclickfix(**kwargs):
    from ebdata.scrapers.general.seeclickfix.seeclickfix_retrieval import SeeClickFixNewsFeedScraper
    return SeeClickFixNewsFeedScraper().update()

def do_georeport(**kwargs):
    url = 'https://mayors24.cityofboston.gov:6443/api/open311/v2/'
    from ebdata.scrapers.general.open311.georeportv2 import GeoReportV2Scraper
    scraper = GeoReportV2Scraper(api_url=url,
                                 http_cache='/tmp/georeport_scraper_cache',
                                 )
    return scraper.update()

def do_events(**kwargs):
    from obdemo.scrapers.add_events import main
    return main()

def do_news(**kwargs):
    from obdemo.scrapers.add_news import main
    main(["http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&subject=massachusetts&scope=bonzai&count=400"])
    main(["http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&scope=blogs&count=400&subject=massachusetts&format=atom"])


def do_police_reports(**kwargs):
    from ebdata.scrapers.us.ma.boston.police_reports.retrieval import BPDNewsFeedScraper
    return BPDNewsFeedScraper().update()

def do_building_permits(**kwargs):
    from ebdata.scrapers.us.ma.boston.building_permits.retrieval import PermitScraper
    return PermitScraper().update()

def do_restaurants(**kwargs):
    from ebdata.scrapers.us.ma.boston.restaurants import retrieval
    return retrieval.RestaurantScraper().update()

def do_aggregates(**kwargs):
    from ebpub.db.bin import update_aggregates
    return update_aggregates.update_all_aggregates(**kwargs)


env = {'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', 'obdemo.settings')}

TASKS = (
    # Tuples like (time_callback, function_to_run, {keyword args}, {environ})
    #
    # The time_callback should take a datetime instance and return True
    # if the function_to_run should be run, and False otherwise.
    #
    # The environ should include DJANGO_SETTINGS_MODULE, if os.environ
    # doesn't already have it.
    #
    # Example:
    # (multiple_daily(12, 0), run_some_function, {'arg': 'foo'}, {'DJANGO_SETTINGS_MODULE': 'foo.settings'})
    (multiple_hourly(*range(0, 60, 20)), do_news, {}, env),
    (multiple_hourly(*range(5, 60, 20)), do_seeclickfix, {}, env),
    (multiple_hourly(*range(7, 60, 20)), do_georeport, {}, env),
    (multiple_hourly(*range(10, 60, 20)), do_events, {}, env),
    (multiple_hourly(*range(15, 60, 20)), do_police_reports, {}, env),

    (multiple_daily(7, 3), do_restaurants, {}, env),

    # (multiple_daily(5, 19), do_building_permits, {}, env),

    (multiple_hourly(*range(9, 60, 7)), do_aggregates, {'verbose': False}, env),
)


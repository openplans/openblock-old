"""
Sample config file for the updaterdaemon.

"""

import os
from ebdata.retrieval.updaterdaemon.config import multiple_hourly, daily
from ebdata.retrieval.updaterdaemon.config import every_n_minutes

def do_seeclickfix(**kwargs):
    from obdemo.scrapers.seeclickfix_retrieval import SeeClickFixNewsFeedScraper
    return SeeClickFixNewsFeedScraper().update()

def do_events(**kwargs):
    from obdemo.scrapers.add_events import main
    return main()

def do_news(**kwargs):
    from obdemo.scrapers.add_news import main
    main()
    main(["http://search.boston.com/search/api?q=*&sort=-articleprintpublicationdate&scope=blogs&count=400&subject=massachusetts&format=atom"])


def do_press_releases(**kwargs):
    from obdemo.scrapers.bpdnews_retrieval import BPDNewsFeedScraper
    return BPDNewsFeedScraper().update()

def do_restaurants(**kwargs):
    from everyblock.cities.boston.restaurants import retrieval
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
    # (daily(12, 0), run_some_function, {'arg': 'foo'}, {'DJANGO_SETTINGS_MODULE': 'foo.settings'})
    (multiple_hourly(0, 20, 40), do_news, {}, env),
    (multiple_hourly(5, 25, 45), do_seeclickfix, {}, env),
    (multiple_hourly(10, 30, 50), do_events, {}, env),
    (multiple_hourly(15, 35, 55), do_press_releases, {}, env),
    (daily(3, 0), do_restaurants, {}, env),

    # Run every 7 minutes (roughly).
    (multiple_hourly(*range(7, 60, 7)), do_aggregates, {'verbose': False}, env),
)

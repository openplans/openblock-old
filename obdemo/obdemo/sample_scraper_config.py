"""
Sample config file for the updaterdaemon.

"""

import os
from ebdata.retrieval.updaterdaemon.config import hourly

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
    (hourly(*range(0, 60, 15)), do_news, {}, env),
    (hourly(*range(1, 60, 15)), do_seeclickfix, {}, env),
    (hourly(*range(2, 60, 15)), do_events, {}, env),
    (hourly(*range(3, 60, 15)), do_press_releases, {}, env),

    (hourly(*range(4, 60, 15)), do_aggregates, {'verbose': False}, env),
)


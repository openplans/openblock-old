"""
Sample config file for the updaterdaemon.


"""


from ebdata.retrieval.updaterdaemon.config import hourly

def do_seeclickfix(**kwargs):
    from obdemo.scrapers.seeclickfix_retrieval import SeeClickFixNewsFeedScraper
    return SeeClickFixNewsFeedScraper().update()

def do_aggregates(**kwargs):
    from ebpub.db.bin import update_aggregates
    return update_aggregates.update_all_aggregates(**kwargs)

env = {'DJANGO_SETTINGS_MODULE': 'obdemo.settings'}

TASKS = (
    # Tuples like (time_callback, function_to_run, {keyword args}, {environ})
    #
    # The time_callback should take a datetime instance and return True
    # if the function_to_run should be run, and False otherwise.
    #
    # The environ should include DJANGO_SETTINGS_MODULE.
    #
    # Example:
    # (daily(12, 0), run_some_function, {'arg': 'foo'}, {'DJANGO_SETTINGS_MODULE': 'foo.settings'})
    (hourly(*range(0, 60, 2)), do_seeclickfix, {}, env),
    (hourly(*range(1, 60, 2)), do_aggregates, {'verbose': True}, env),
)


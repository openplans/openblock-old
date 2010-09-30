"""
Sample config file for the updaterdaemon.


"""


def hourly(*minutes):
    def handle(dt):
        return dt.minute in minutes
    return handle

def multiple_hourly(*hour_minutes):
    # hour_minutes is a list of tuples in the format (hour, minute)
    hour_minutes = set(hour_minutes)
    def handle(dt):
        return (dt.hour, dt.minute) in hour_minutes
    return handle

def daily(hour, minute):
    def handle(dt):
        return dt.hour == hour and dt.minute == minute
    return handle

def weekly(weekday, hour, minute):
    # weekday -- 0=Monday, 6=Sunday
    def handle(dt):
        return dt.weekday() == weekday and dt.hour == hour and dt.minute == minute
    return handle

def once(*args):
    """useful for testing; this one handles the first minute it's passed,
    and returns false for all future minutes.
    """
    class OneShotHandler:
        has_run = False
        def handle(self, dt):
            if not self.has_run:
                self.has_run = True
                return True
            return False
    return OneShotHandler().handle


def do_seeclickfix(**kwargs):
    from obdemo.scrapers.seeclickfix_retrieval import SeeClickFixNewsFeedScraper
    return SeeClickFixNewsFeedScraper().update()

def do_aggregates(**kwargs):
    from ebpub.db.bin import update_aggregates
    return update_aggregates.update_all_aggregates(**kwargs)

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
    (once(), do_seeclickfix, {}, {'DJANGO_SETTINGS_MODULE': 'obdemo.settings'}),

    (once(), do_aggregates, {'verbose': True}, {'DJANGO_SETTINGS_MODULE': 'obdemo.settings'}),
)


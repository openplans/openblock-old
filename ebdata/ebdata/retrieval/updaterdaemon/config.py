"""
Sample config file for the updaterdaemon.

Also contains useful callback generators that check whether to handle
a particular datetime.
"""

import datetime


def multiple_hourly(*minutes):
    """
    Returns a checker that matches datetimes every hour, at the given
    minute(s).
    """
    def handle(dt):
        return dt.minute in minutes
    return handle

def multiple_daily(*hour_minutes):
    """
    Returns a checker that matches multiple times every day, at the
    given (hour, minute) time(s).
    """
    hour_minutes = set(hour_minutes)
    def handle(dt):
        return (dt.hour, dt.minute) in hour_minutes
    return handle

def daily(hour, minute):
    """
    Returns a checker that matches once a day at the given hour & minute.
    """
    def handle(dt):
        return dt.hour == hour and dt.minute == minute
    return handle

def weekly(weekday, hour, minute):
    """
    Returns a checker that matches datetimes once a week, at the given
    weekday (0=sunday), hour, and minute.
    """
    def handle(dt):
        return dt.weekday() == weekday and dt.hour == hour and dt.minute == minute
    return handle

def once(*args):
    """Useful for testing: returns a checker that matches the first
    datetime that's passed to it, and then returns False forever
    after.  (Note that reloading config defeats this.)
    """
    class OneShotHandler:
        has_run = False
        def handle(self, dt):
            if not self.has_run:
                self.has_run = True
                return True
            return False
    return OneShotHandler().handle



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
)


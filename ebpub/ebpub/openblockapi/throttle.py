"""
Throttle implementation borrowed from Django-Tastypie
http://github.com/toastdriven/django-tastypie/

Copyright 2011 Daniel Lindsley.  BSD license.
"""

import time
from django.core.cache import cache

class BaseThrottle(object):
    """
    A simplified, swappable base class for throttling.
    
    Does nothing save for simulating the throttling API and implementing
    some common bits for the subclasses.
    
    Accepts a number of optional kwargs::
    
        * ``throttle_at`` - the number of requests at which the user should
          be throttled. Default is 150 requests.
        * ``timeframe`` - the length of time (in seconds) in which the user
          make up to the ``throttle_at`` requests. Default is 3600 seconds (
          1 hour).
        * ``expiration`` - the length of time to retain the times the user
          has accessed the api in the cache. Default is 604800 (1 week).
    """
    def __init__(self, throttle_at=150, timeframe=3600, expiration=None):
        self.throttle_at = throttle_at
        # In seconds, please.
        self.timeframe = timeframe
        
        if expiration is None:
            # Expire in a week.
            expiration = 604800
        
        self.expiration = int(expiration)
    
    def convert_identifier_to_key(self, identifier):
        """
        Takes an identifier (like a username or IP address) and converts it
        into a key usable by the cache system.
        """
        bits = []
        
        for char in identifier:
            if char.isalnum() or char in ['_', '.', '-']:
                bits.append(char)
        
        safe_string = ''.join(bits)
        return "%s_accesses" % safe_string
    
    def should_be_throttled(self, identifier, **kwargs):
        """
        Returns whether or not the user has exceeded their throttle limit.
        
        Always returns ``False``, as this implementation does not actually
        throttle the user.
        """
        return False
    
    def accessed(self, identifier, **kwargs):
        """
        Handles recording the user's access.
        
        Does nothing in this implementation.
        """
        pass


class CacheThrottle(BaseThrottle):
    """
    A throttling mechanism that uses just the cache.
    """
    def should_be_throttled(self, identifier, **kwargs):
        """
        Returns whether or not the user has exceeded their throttle limit.
        
        Maintains a list of timestamps when the user accessed the api within
        the cache.
        
        Returns ``False`` if the user should NOT be throttled or ``True`` if
        the user should be throttled.
        """
        key = self.convert_identifier_to_key(identifier)
        
        # Make sure something is there.
        cache.add(key, [])
        
        # Weed out anything older than the timeframe.
        minimum_time = int(time.time()) - int(self.timeframe)
        times_accessed = [access for access in cache.get(key, ()) if access >= minimum_time]
        cache.set(key, times_accessed, self.expiration)
        
        if len(times_accessed) >= int(self.throttle_at):
            # Throttle them.
            return True
        
        # Let them through.
        return False
    
    def accessed(self, identifier, **kwargs):
        """
        Handles recording the user's access.
        
        Stores the current timestamp in the "accesses" list within the cache.
        """
        key = self.convert_identifier_to_key(identifier)
        times_accessed = cache.get(key, [])
        times_accessed.append(int(time.time()))
        cache.set(key, times_accessed, self.expiration)

    def seconds_till_unthrottling(self, identifier):
        """
        New feature for OpenBlock: try to figure out when the user will be un-throttled.
        """
        key = self.convert_identifier_to_key(identifier)
        times_accessed = cache.get(key, [])
        if not times_accessed:
            return 0
        # Assume we have already weeded out anything older than the timeframe.
        oldest = times_accessed[0]
        when = oldest + self.timeframe
        return when - int(time.time())


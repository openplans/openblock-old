from ebpub.geocoder.base import AmbiguousResult
from ebpub.geocoder.base import GeocodingException

from utils import log_exception
import logging
logger = logging.getLogger()

def quick_dirty_fallback_geocode(addr, parse=True):
    """
    Try to get SOME x,y even with bad blocks data,
    by falling back to external geocoders.
    """
    from ebdata.nlp.addresses import parse_addresses
    from ebpub.geocoder import SmartGeocoder
    if parse:
        addrs = parse_addresses(addr)
    else:
        addrs = [addr]
    for addr, unused in addrs:
        try:
            try:
                result = SmartGeocoder().geocode(addr)
                point = result['point']
                logger.debug("internally geocoded %r" % addr)
                return point.x, point.y
            except GeocodingException:
                logger.debug("internal geocoder failed on %r:\n" % addr)
                log_exception(level=logging.DEBUG)
                x,y = None, None
                # XXX Don't bother, external geocoding rarely gives us
                # anything inside Boston now that we have decent
                # blocks data.  But I want to preserve this script for
                # now till we figure out what to do with geocoding
                # more generally
                continue
        except:
            logger.error('uncaught geocoder exception on %r\n' % addr)
            log_exception()

    return None, None

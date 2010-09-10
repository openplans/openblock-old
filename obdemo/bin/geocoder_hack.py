from ebpub.geocoder import AmbiguousResult
from utils import log_exception
import sys

def quick_dirty_fallback_geocode(addr, parse=True):
    """
    Try to get SOME lat,lon even with bad blocks data,
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
                print "YAY internally geocoded %r" % addr
                return point.x, point.y
            except:
                x,y = None, None
                sys.stderr.write("BOO internal geocoder failed on %r:\n" % addr)
                log_exception()
            if None in (x, y):
                # XXX log something
                # Other geocoders need to know the city
                addr += ', Boston, MA'
                from geopy import geocoders
                g = geocoders.Google(resource='maps', output_format='json')
                import urllib2
                try:
                    for unused, (lat, lon) in g.geocode(addr, exactly_one=False):
                        print "YAY google geocoded %r" % addr
                        return (lon, lat)
                except urllib2.HTTPError:
                    # Rate throttled? Try another.
                    pass
                except ValueError:
                    # Bad JSON response? why?
                    pass
                us = geocoders.GeocoderDotUS()
                for unused, (lat, lon) in us.geocode(addr, exactly_one=False):
                    print "YAY geocoder.us geocoded %r" % addr
                    return (lon, lat)
        except:
            sys.stderr.write( '===== uncaught geocoder exception on %r\n' % addr)
            log_exception()
            sys.stderr.write('======================\n')

    return None, None

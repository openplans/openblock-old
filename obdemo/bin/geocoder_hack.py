def quick_dirty_fallback_geocode(addr, parse=True):
    """
    Try to get SOME lat,lon even with bad blocks data,
    by falling back to external geocoder.
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
                #x,y = SmartGeocoder().geocode(addr)
                #return x, y
                raise Exception('useless till we get more blocks')
            except:
                # XXX log something
                # Other geocoders need to know the city
                addr += ', Boston, MA'
                from geopy import geocoders
                g = geocoders.Google(resource='maps', output_format='json')
                import urllib2
                try:
                    for unused, (lat, lon) in g.geocode(addr, exactly_one=False):
                        print "YAY geocoded %r" % addr
                        return (lon, lat)
                except urllib2.HTTPError:
                    # Rate throttled? Try another.
                    pass
                us = geocoders.GeocoderDotUS()
                for unused, (lat, lon) in us.geocode(addr, exactly_one=False):
                    print "YAY geocoded %r" % addr
                    return (lon, lat)
                raise
        except:
            # XXX log something
            print '  geocoder exception on %r' % addr
    return None, None

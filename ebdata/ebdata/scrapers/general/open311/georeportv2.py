from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Polygon
from ebpub.db.models import Schema, SchemaField, NewsItem, Lookup
from ebpub.geocoder.reverse import reverse_geocode
from ebpub.metros.allmetros import get_metro
from httplib2 import Http
from lxml import etree
import datetime
import pyrfc3339
import time
import traceback
import urllib

import logging
log = logging.getLogger(__name__)

class GeoReportV2Scraper(object): 

    def __init__(self, api_url, api_key=None, jurisdiction_id=None, 
                 schema_slug='open311-service-requests', http_cache=None,
                 seconds_between_requests=2.0, days_prior=90,
                 bounds=None,
                 make_html_url=False):
        """
        If ``bounds`` is passed, it should be a geometry; news items
        that don't intersect with that geometry will be skipped.
        Default bounds is the extent defined in settings.METRO_LIST.

        If ``make_html_url`` is true, we will assume that the provider
        supports human-readable versions of the 311 request by changing
        the extension to .html, and use that as our NewsItem.url.
        This is not really part of the GeoReport v2 API, but
        SeeClickFix supports it.
        """
        self.api_url = api_url
        if not self.api_url.endswith('/'): 
            self.api_url += '/'
 
        self.days_prior = days_prior
        self.seconds_between_requests = seconds_between_requests
        self.schema_slug = schema_slug
        self.schema = Schema.objects.get(slug=self.schema_slug)
        self.service_request_id_field = SchemaField.objects.get(schema=self.schema, name='service_request_id')
        
        self.standard_params = {}
        if api_key is not None: 
            self.standard_params['api_key'] = api_key
        if jurisdiction_id is not None: 
            self.standard_parms['jurisdiction_id'] = jurisdiction_id
        
        self.http = Http(http_cache)
        self.bounds = bounds
        if bounds is None:
            log.info("Calculating geographic boundaries from the extent in setttings.METRO_LIST")
            extent = get_metro()['extent']
            self.bounds = Polygon.from_bbox(extent)
        self.make_html_url = make_html_url

    def service_requests_url(self, start_date, end_date):
        params = dict(self.standard_params)
        params['start_date'] = pyrfc3339.generate(start_date, utc=True, accept_naive=True)
        params['end_date'] = pyrfc3339.generate(end_date, utc=True, accept_naive=True)
        return self.api_url + 'requests.xml?' + urllib.urlencode(params)
    
    def update(self, min_date=None, request_granularity=datetime.timedelta(days=1)):
        now = datetime.datetime.utcnow()
        if min_date is None:
            # default is midnight 90 days ago.
            # use midnight so progressive request urls will 
            # be the same over time, and theoretically should
            # be cacheable.
            start_date = now - datetime.timedelta(days=self.days_prior)
            start_date = datetime.datetime(start_date.year, 
                                           start_date.month,
                                           start_date.day,
                                           0,0,0)
        else: 
            start_date = min_date
            
        while (start_date < now):
            end_date = start_date + request_granularity
            log.info("Fetching from %s - %s" % (start_date, end_date))
            url = self.service_requests_url(start_date, end_date)
            self._update(url)
            start_date = end_date
            time.sleep(self.seconds_between_requests)
    
    def _update(self, url):
        
        # make http request to api
        try: 
            log.debug("Requesting %s" % url)
            # User-Agent is a lame workaround for SeeClickFix blocking httplib2
            # (they had too many bots hitting them).
            response, content = self.http.request(url, headers={'User-Agent': 'openblock-georeport-scraper'})
            if response.status != 200: 
                log.error("Error retrieving %s: status was %d" % (url, response.status))
                log.error(content)
                return
        except:
            log.error("Error retrieving %s: %s" % (url, traceback.format_exc()))
            return
        log.info("Got %s OK" % url)

        # parse the response
        try: 
            root = etree.XML(content)
        except: 
            log.error("Error parsing response from %s (%s): %s" % (url, content, traceback.format_exc()))
            return
            
        # iterate through the service requests in the response
        reqs = root.findall('.//request')
        if not reqs:
            log.warn("No request elements found")
        for req in reqs:
            self._update_service_request(req)

    def _update_service_request(self, sreq):
        service_request_id = self._get_request_field(sreq, 'service_request_id')

        if not service_request_id:
            log.warning("Skipping request with no request id (may be in progress)!")
            return


        # pull out the location first, if we can't do this, we don't want it.
        try:
            point = Point(float(sreq.find('long').text), 
                          float(sreq.find('lat').text),
                          srid=4326)
        except: 
            log.debug("Skipping request with invalid location (%s)" % service_request_id)
            return
        if self.bounds is not None:
            if not self.bounds.intersects(point):
                log.debug("Skipping request at %s, outside bounds" % point)
                return
        try:
            ni = NewsItem.objects.filter(schema=self.schema).by_attribute(self.service_request_id_field, 
                                                                          service_request_id).all()[0]
            log.info('updating existing request %s' % service_request_id)
        except IndexError:
            # create the NewsItem
            ni = NewsItem(schema=self.schema)
            log.info('created new service request %s' % service_request_id)

        ni.title = self._get_request_field(sreq, 'service_name')
        ni.description = self._get_request_field(sreq, 'description')
        ni.location = point
        # try to reverse geocde this point
        try: 
            block, distance = reverse_geocode(ni.location)
            ni.location_name = block.pretty_name
            ni.block = block
        except: 
            log.debug("Failed to reverse geocode item %s" % service_request_id)
        
        # try to pull the requested_datetime into pubdate/itemdate
        # default to now.
        try: 
            ni.pub_date = pyrfc3339.parse(sreq.find('requested_datetime').text)
        except:
            ni.pub_date = datetime.datetime.utcnow()
            log.warning("Filling in current time for pub_date on item with no requested_datetime (%s)" % service_request_id)
        ni.item_date = datetime.date(ni.pub_date.year, ni.pub_date.month, ni.pub_date.day)

        if self.make_html_url:
            ni.url = '%srequests/%s.html' % (self.api_url, service_request_id)
        else:
            # try to pull the 'media' url out into url, for lack of a better one currently
            ni.url = self._get_request_field(sreq, 'media_url')
        ni.save()

        ni.attributes['service_request_id'] = service_request_id

        # varchar / text fields
        for fieldname in ('request_id', 'service_code', 'address_id',
                          'media_url', 'status_notes', 'service_notice'):

            val = self._get_request_field(sreq, fieldname)
            if val != '':
                ni.attributes[fieldname] = val
        
        # datetime fields
        for fieldname in ('expected_datetime', 'requested_datetime'):
            val = self._get_request_field(sreq, fieldname)
            if val == '':
                continue

            # try to parse it
            try:
                ni.attributes[fieldname] = pyrfc3339.parse(val) 
            except ValueError: 
                # invalid date, just omit
                log.warning('Omitting invalid datetime field %s = %s' % (fieldname, val))
                pass
        
        # lookups 
        for fieldname in ('service_name', 'agency_responsible', 'status'):
            val = self._get_request_field(sreq, fieldname)
            if val == '': 
                ni.attributes[fieldname] = self._lookup_for(fieldname, 'Unknown')
            ni.attributes[fieldname] = self._lookup_for(fieldname, val)
            
    def _get_request_field(self, request, fieldname):
        val = request.find(fieldname)
        if val is None: 
            return ''
        return (val.text or '').strip()
        
    def _lookup_for(self, fieldname, value):
        sf = SchemaField.objects.get(schema=self.schema, name=fieldname)
        lo = Lookup.objects.get_or_create_lookup(sf, value, make_text_slug=False)
        return lo.slug

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option(
        "-k", "--api-key", help='GeoReport V2 API key', action='store',
        )
    parser.add_option(
        "--make-html-url",
        help='save URLs based on replacing the API resource extension with .html',
        action='store_true',
        )
    parser.add_option(
        "--days-prior", help='how many days ago to start scraping', type="int",
        )
    import sys
    options, args = parser.parse_args(sys.argv)
    scraper = GeoReportV2Scraper(api_url=args[1], api_key=options.api_key,
                                 days_prior=options.days_prior,
                                 make_html_url=options.make_html_url)
    scraper.update()

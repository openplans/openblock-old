#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

# TODO: Rewrite using https://github.com/codeforamerica/three ?
# Looks much simpler, if it works well.

from django.contrib.gis.geos import Point
from ebpub.utils.geodjango import get_default_bounds
from ebpub.db.models import Schema, SchemaField, NewsItem, Lookup
from ebpub.geocoder.reverse import reverse_geocode
from httplib2 import Http
from lxml import etree
import datetime
import pyrfc3339
import socket
import sys
import time
import traceback
import urllib

import logging
log = logging.getLogger('eb.retrieval.georeportv2')

class GeoReportV2Scraper(object): 

    def __init__(self, api_url, api_key=None, jurisdiction_id=None, 
                 schema_slug='open311-service-requests', http_cache=None,
                 seconds_between_requests=2.0, days_prior=90,
                 timeout=60,
                 bounds=None,
                 html_url_template=None):
        """
        If ``bounds`` is passed, it should be a geometry; news items
        that don't intersect with that geometry will be skipped.
        Default bounds is the extent defined in settings.METRO_LIST.

        If ``html_url_template`` is given, the service_request id is 
        replaced into the string to form the news item's url. eg
        http://somewhere/%s.html.  This is not really part of the GeoReport v2 API, but
        in some cases, like SeeClickFix, there is a well known location based on 
        the identifier for an item.
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
        
        self.http = Http(http_cache, timeout=timeout)
        self.bounds = bounds
        if bounds is None:
            log.info("Calculating geographic boundaries from the extent in settings.METRO_LIST")
            self.bounds = get_default_bounds()
            try:
                # Make sure it's a geos geometry, not an ogr/gdal geometry,
                # so we can test for intersecting geos Points.
                self.bounds = self.bounds.geos
            except AttributeError:
                pass
        self.html_url_template = html_url_template

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
            # Pagination is not officially part of the v2 spec, but
            # some endpoints support it, eg. seeclickfix has a non-compliant
            # page size of 20.
            page = 1
            while True:
                items_on_page = self._update(url + '&page=%d' % page)
                time.sleep(self.seconds_between_requests)
                if not items_on_page:
                    break
                page += 1
            start_date = end_date

    def _update(self, url):
        """Make an HTTP request to url, create newsitems,
        return number of items found (not created)
        """
        # make http request to api
        try: 
            log.debug("Requesting %s" % url)
            # User-Agent is a lame workaround for SeeClickFix blocking httplib2
            # (they had too many bots hitting them).
            response, content = self.http.request(url, headers={'User-Agent': 'openblock-georeport-scraper'})
            if response.status != 200:
                log.error("Error retrieving %s: status was %d" % (url, response.status))
                log.error(content)
                return 0
        except socket.error:
            log.error("Couldn't connect to %s" % url)
        except:
            log.error("Unhandled error retrieving %s: %s" % (url, traceback.format_exc()))
            return 0
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
            log.info("No request elements found")
        if response.fromcache:
            log.info("Requests from this time period are unchanged since last update (cached)")
        else:
            for req in reqs:
                self._update_service_request(req)
        return len(list(reqs))

    def _update_service_request(self, sreq):
        service_request_id = self._get_request_field(sreq, 'service_request_id')

        if not service_request_id:
            log.info("Skipping request with no request id (may be in progress)!")
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
        ni.location_name = self._get_request_field(sreq, 'address')
        # try to reverse geocde this point
        if not ni.location_name:
            try:
                block, distance = reverse_geocode(ni.location)
                ni.location_name = block.pretty_name
            except:
                log.debug("Failed to reverse geocode item %s" % service_request_id)

        # try to pull the requested_datetime into pubdate/itemdate
        # default to now.
        try: 
            ni.pub_date = pyrfc3339.parse(sreq.find('requested_datetime').text)
        except:
            ni.pub_date = datetime.datetime.utcnow()
            log.info("Filling in current time for pub_date on item with no requested_datetime (%s)" % service_request_id)
        ni.item_date = datetime.date(ni.pub_date.year, ni.pub_date.month, ni.pub_date.day)

        if self.html_url_template:
            ni.url = self.html_url_template.replace('{id}', service_request_id)
            log.info('Assigning html url "%s" to %s' % (ni.url, service_request_id))

        ni.save()

        ni.attributes['service_request_id'] = service_request_id

        # varchar fields
        for fieldname in ('request_id', 'service_code', 'address_id',
                          'media_url', 'status_notes', 'service_notice'):
            val = self._get_request_field(sreq, fieldname)
            if val != '':
                if len(val) < 4096:
                    ni.attributes[fieldname] = val
                else: 
                    log.info("truncating value for %s (%s)" % (fieldname, val))
                    ni.attributes[fieldname] = val[0:4096]

        # text fields
        for fieldname in ('service_notice'):
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
                log.info('Omitting invalid datetime field %s = %s' % (fieldname, val))
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

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    from optparse import OptionParser
    usage = "usage: %prog [options] <api url>"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-k", "--api-key", help='GeoReport V2 API key', action='store',
        )
    parser.add_option(
        "--html-url-template",
        help='template for creating html urls for items based on their identifiers, eg http://example.com/{id}.html',
        action='store'
        )
    parser.add_option(
        "--days-prior", help='how many days ago to start scraping', type="int",
        default=90
        )
    parser.add_option(
        "--schema", help="slug of news item type to use",
        default="open311-service-requests"
        )
    parser.add_option(
        "--http-cache", help='location to use as an http cache.  If a cached value is seen, no update is performed.', 
        action='store'
        )
    parser.add_option(
        "--jurisdiction-id", help='jurisdiction identifier to provide to api',
        action='store'
        )

    from ebpub.utils.script_utils import add_verbosity_options, setup_logging_from_opts
    add_verbosity_options(parser)

    options, args = parser.parse_args(argv)
    setup_logging_from_opts(options, log)

    if len(args) < 1:
        parser.print_usage()
        return 1
    
    scraper = GeoReportV2Scraper(api_url=args[0], api_key=options.api_key,
                                 jurisdiction_id=options.jurisdiction_id,
                                 schema_slug=options.schema,
                                 days_prior=options.days_prior,
                                 http_cache=options.http_cache,
                                 html_url_template=options.html_url_template)
    scraper.update()
    return 0


if __name__ == '__main__':
    sys.exit(main())

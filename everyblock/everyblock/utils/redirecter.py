#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of everyblock
#
#   everyblock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   everyblock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with everyblock.  If not, see <http://www.gnu.org/licenses/>.
#

from django.http import Http404, HttpResponse
import urllib

def redirecter(request):
    "Redirects to a given URL without sending the 'Referer' header."
    try:
        url = request.GET['url']
    except KeyError:
        raise Http404
    if not url.startswith('http://') and not url.startswith('https://'):
        raise Http404
    return HttpResponse('<html><head><meta http-equiv="Refresh" content="0; URL=%s"></head><body>Loading...</body></html>' % urllib.unquote_plus(url))

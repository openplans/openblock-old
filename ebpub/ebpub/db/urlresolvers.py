#   Copyright 2011 OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

from django.core import urlresolvers
import posixpath
import urllib

def filter_reverse(slug, args):
    """Generate a reverse schema_filter URL.
    """
    for i, a  in enumerate(args):
        if isinstance(a, tuple) or isinstance(a, list):
            # The first item is the arg name, the rest are arg values.
            if len(a) > 1:
                name = a[0]
                values = ','.join(a[1:])
                args[i] = (name, values)
            else:
                # No values.
                # This is allowed eg. for showing a list of available
                # Blocks, or Lookup values, etc.
                args[i] = (a[0], '')
        else:
            raise TypeError("Need a list or tuple, got: %s" % a)

    url = urlresolvers.reverse('ebpub-schema-filter', args=[slug])
    # Normalize duplicate slashes, dots, and the like.
    url = posixpath.normpath(url) + '/'
    if args:
        # Normalize a bit.
        args = sorted(args)
        querystring = urllib.urlencode(args)
        url = '%s?%s' % (url, querystring)
    return url


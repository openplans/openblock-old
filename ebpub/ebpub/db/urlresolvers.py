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

def filter_reverse(slug, args):
    """Generate a reverse schema_filter URL.
    """
    for i, a  in enumerate(args):
        if isinstance(a, tuple) or isinstance(a, list):
            # The first item is the arg name, the rest are arg values.
            if len(a) > 1:
                name = a[0]
                values = ','.join(a[1:])
                args[i] = '%s=%s' % (name, values)
            else:
                # This is allowed eg. for showing a list of available
                # Blocks, or Lookup values, etc.
                args[i] = a[0]
        else:
            assert isinstance(a, basestring)
    #argstring = urllib.quote(';'.join(args)) #['%s=%s' % (k, v) for (k, v) in args])
    argstring = ';'.join(args) #['%s=%s' % (k, v) for (k, v) in args])

    if not argstring.lstrip('/').startswith('filter'):
        argstring = 'filter/%s' % argstring
    url = urlresolvers.reverse('ebpub-schema-filter', args=[slug])
    url = '%s/%s/' % (url, argstring)
    # Normalize duplicate slashes, dots, and the like.
    url = posixpath.normpath(url) + '/'
    return url


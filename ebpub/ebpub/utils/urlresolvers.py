#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
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

"""
Django URL resolvers that take into account the value of get_metro().

TODO: Currently, get_metro() is called and calculated each time through the
URL patterns, which could be inefficient. Look for a better way of doing this.
"""

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import RegexURLPattern
from django.core.urlresolvers import RegexURLResolver
from ebpub.metros.allmetros import get_metro

class MulticityRegexURLPattern(RegexURLPattern):
    def resolve(self, path):
        if not get_metro()['multiple_cities']:
            return None
        return RegexURLPattern.resolve(self, path)

class SinglecityRegexURLPattern(RegexURLPattern):
    def resolve(self, path):
        if get_metro()['multiple_cities']:
            return None
        return RegexURLPattern.resolve(self, path)

def metro_patterns(multi, single):
    pattern_list = []
    for t in multi:
        pattern_list.append(url(MulticityRegexURLPattern, *t))
    for t in single:
        pattern_list.append(url(SinglecityRegexURLPattern, *t))
    return pattern_list

def url(klass, regex, view, kwargs=None, name=None, prefix=''):
    # Unused?? Delete this?
    if type(view) == list:
        # For include(...) processing.
        return RegexURLResolver(regex, view[0], kwargs)
    else:
        if isinstance(view, basestring):
            if not view:
                raise ImproperlyConfigured('Empty URL pattern view name not permitted (for pattern %r)' % regex)
            if prefix:
                view = prefix + '.' + view
        return klass(regex, view, kwargs, name)


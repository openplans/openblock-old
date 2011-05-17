#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
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

import re

class Hole(object):

    # This would have been a good place for a docstring
    # mentioning something about what the heck a Hole is for.
    # Thanks guys.

    capture = True # Designates whether the Hole captures something in regex().
    def __eq__(self, other):
        "A Hole is equal to any other Hole (but not subclasses)."
        return type(other) is self.__class__

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def regex(self):
        return '(.*?)'

class OrHole(Hole):
    "A Hole that can contain one of a set of values."
    capture = True
    def __init__(self, *choices):
        self.choices = choices

    def __eq__(self, other):
        "An OrHole is equal to another one if its choices are the same."
        return type(other) is self.__class__ and self.choices == other.choices

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self.choices)

    def regex(self):
        return '(%s)' % '|'.join(re.escape(choice) for choice in self.choices)

class RegexHole(Hole):
    """
    A Hole that contains data that matches the given regex. It's up to the
    caller to determine whether the data should be grouped.
    """
    def __init__(self, regex_string, capture):
        self.regex_string = regex_string
        self.capture = capture

    def __eq__(self, other):
        "A RegexHole is equal to another one if its regex_string is the same."
        return type(other) is self.__class__ and self.regex_string == other.regex_string and self.capture == other.capture

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.regex_string)

    def regex(self):
        return self.regex_string

class IgnoreHole(Hole):
    """
    A Hole that contains an arbitrary amount of data but should be ignored.
    I.e., its contents are *not* included in extract().
    """
    capture = False
    def regex(self):
        return '.*?' # No parenthesis!

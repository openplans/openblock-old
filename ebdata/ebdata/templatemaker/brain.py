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

from listdiff import Hole # relative import
import re

class Brain(list):

    # This would have been a good place for a docstring
    # mentioning something about what the heck a Brain is for.
    # Thanks guys.

    def _each_member(self):
        for s in self:
            yield isinstance(s, Hole), s

    def as_text(self, custom_marker='{{ HOLE }}'):
        """
        Returns a display-friendly version of the Brain, using the
        given custom_marker to mark template holes.
        """
        output = []
        for is_hole, member in self._each_member():
            if is_hole:
                output.append(custom_marker)
            else:
                output.append(member)
        return ''.join(output)

    def concise(self):
        """
        Returns the brain as a list with all consecutive strings combined into
        a single string.
        """
        last_one_was_string = False
        output = []
        for is_hole, member in self._each_member():
            if is_hole:
                output.append(member)
            else:
                if last_one_was_string:
                    output[-1] += member
                else:
                    output.append(member)
            last_one_was_string = not is_hole
        return output

    def num_holes(self):
        """
        Returns the number of holes in this Brain.
        """
        return len([member for is_hole, member in self._each_member() if is_hole])

    def match_regex(self):
        """
        Returns a regular expression (as a string) that matches strings
        formatted with this Brain.
        """
        regex = ['^(?s)']
        for is_hole, member in self._each_member():
            if is_hole:
                regex.append(member.regex())
            else:
                regex.append(re.escape(member))
        regex.append('$')
        return ''.join(regex)

    def serialize(self):
        """
        Returns a serialized string representing this Brain.
        """
        import cPickle as pickle
        import base64
        return base64.encodestring(pickle.dumps(self, protocol=2))

    def from_serialized(cls, serialized_string):
        """
        Class method that returns a Brain instance for the given serialized
        string (as returned by Brain.serialize()).
        """
        import cPickle as pickle
        import base64
        return pickle.loads(base64.decodestring(serialized_string))
    from_serialized = classmethod(from_serialized)

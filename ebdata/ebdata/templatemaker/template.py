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

from brain import Brain # relative import
from listdiff import listdiff # relative import
import re

class NoMatch(Exception):
    pass

class Template(object):
    def __init__(self, brain=None):
        if isinstance(brain, str):
            self.brain = Brain.from_serialized(brain)
        else:
            self.brain = brain

    def tokenize(self, text):
        """
        Returns a list of tokens for the given text. This list may include
        Hole instances.
        """
        return list(text)

    def learn(self, *texts):
        """
        Learns the given Sample String(s).
        """
        brain = self.brain
        for text in texts:
            tokens = self.tokenize(text)
            if brain is None:
                brain = Brain(tokens)
            else:
                brain = Brain(listdiff(brain, tokens))
        self.brain = brain

    def as_text(self, custom_marker='{{ HOLE }}'):
        """
        Returns a display-friendly version of the template, using the
        given custom_marker to mark template holes.
        """
        return self.brain.as_text(custom_marker)

    def num_holes(self):
        """
        Returns the number of holes in this template.
        """
        return self.brain.num_holes()

    def extract(self, text):
        """
        Given a bunch of text that is marked up using this template, extracts
        the data.

        Returns a tuple of the raw data, in the order in which it appears in
        the template. If the text doesn't match the template, raises NoMatch.
        """
        regex = self.brain.match_regex()
        m = re.search(regex, text)
        if m:
            return m.groups()
        raise NoMatch()

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

"""
These tests are identical to the ones in listdiff.py but use the C version of
longest_common_substring instead of the pure Python version.
"""

from ebdata.templatemaker.listdiffc import longest_common_subsequence as longest_common_substring
from listdiff import LongestCommonSubstring
import unittest

class LongestCommonSubstringC(LongestCommonSubstring):
    def LCS(self, seq1, seq2):
        return longest_common_substring(seq1, seq2)

del LongestCommonSubstring

if __name__ == "__main__":
    unittest.main()

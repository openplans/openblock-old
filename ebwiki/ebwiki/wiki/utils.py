#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebwiki
#
#   ebwiki is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebwiki is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebwiki.  If not, see <http://www.gnu.org/licenses/>.
#

import re

def wikify(text):
    text = re.sub(r'\[(https?://.*?)\s+(.*?)\]', r'<a href="\1">\2</a>', text)
    text = re.sub(r'\[(\w{1,30})\s+(.*?)\]', r'<a href="/\1/">\2</a>', text)
    text = re.sub(r'\r?\n', '<br />', text)
    text = re.sub(r'(?m)^h(\d)\. (.*?)$', r'<h\1>\2</h\1>', text)
    return text

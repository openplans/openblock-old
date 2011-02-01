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

from ebdata.blobs.models import Page, IgnoredDateline
from ebdata.nlp.datelines import guess_datelines
from ebpub.streets.models import Suburb
import re

def dateline_should_be_purged(dateline):
    dateline = dateline.upper()
    try:
        IgnoredDateline.objects.get(dateline=dateline)
        return True
    except IgnoredDateline.DoesNotExist:
        pass
    try:
        Suburb.objects.get(normalized_name=dateline)
        return True
    except Suburb.DoesNotExist:
        pass
    return False

def all_relevant_datelines():
    """
    Prints all datelines that are in articles but not in ignored_datelines,
    for all unharvested Pages in the system.
    """
    seen = {}
    for page in Page.objects.filter(has_addresses__isnull=True, is_pdf=False):
        for bit in page.mine_page():
            for dateline in guess_datelines(bit):
                dateline = dateline.upper()
                if dateline not in seen and not dateline_should_be_purged(dateline):
                    print dateline
                    seen[dateline] = 1

def page_should_be_purged(paragraph_list):
    """
    Returns a tuple of (purge, reason). purge is True if the given list of
    strings can be safely purged. reason is a string.
    """
    datelines = []
    for para in paragraph_list:
        datelines.extend(guess_datelines(para))
    if datelines:
        dateline_text = ', '.join([str(d) for d in datelines])
        if not [d for d in datelines if not dateline_should_be_purged(d)]:
            return (True, 'Dateline(s) %s safe to purge' % dateline_text)
        else:
            return (False, 'Dateline(s) %s found but not safe to purge' % dateline_text)
    return (False, 'No datelines')

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
Utility functions for munging address/block/street names.
"""

import re
from ebpub.utils.text import smart_title, slugify

def make_street_pretty_name(street, suffix):
    street_name = smart_title(street)
    if suffix:
        street_name += u' %s.' % smart_title(suffix)
    return street_name

def make_block_number(left_from_num, left_to_num, right_from_num, right_to_num):
    """
    Given 4 numbers (left low, left high, right low, right high),
    returns a string indicating the range of lowest to highest.
    "lowest" and "highest" are derived as per the make_block_numbers() function.

    >>> make_block_number(1, 9, 2, 3)
    u'1-9'
    >>> make_block_number(1, 1, 1, 1)
    u'1'
    >>> make_block_number(9, 8, 7, 6)
    u'6-9'

    Zero is not considered part of a range:
    >>> make_block_number(0, 1, 2, 3)
    u'1-3'

    None is ignored, but one non-zero number must be provided:
    >>> make_block_number(None, None, 1, None)
    u'1'
    >>> make_block_number(None, None, None, None)
    Traceback (most recent call last):
    ...
    ValueError: No non-None addresses provided
    >>> make_block_number(0, 0, 0, 0)
    Traceback (most recent call last):
    ...
    ValueError: No non-zero numeric addresses provided in [0, 0, 0, 0]

    """
    lo_num, hi_num = make_block_numbers(left_from_num, left_to_num,
                                        right_from_num, right_to_num)
    if lo_num == hi_num:
        number = unicode(lo_num)
    elif lo_num and not hi_num:
        number = unicode(lo_num)
    elif hi_num and not lo_num:
        number = unicode(hi_num)
    else:
        number = u'%s-%s' % (lo_num, hi_num)
    return number

def make_block_numbers(left_from_num, left_to_num, right_from_num, right_to_num):
    """
    Given four numbers, or strings containing numbers, returns the min
    and max as a pair.

    Because the input is possibly messy and quirky, there are some
    subtleties in what's considered the min and max, see below.  In
    all cases, the motivation is to assume that the input is spelled
    correctly for human reading, no matter how unlikely; but for
    sorting we assume we want a single non-negative number.

    >>> make_block_numbers(10,9,8,7)
    (7, 10)

    >>> make_block_numbers(1,1,1,1)
    (1, 1)

    The first quirk is that zero is ignored:
    >>> make_block_numbers(0,1,2,3)
    (1, 3)

    Another quirk is that negative numbers are compared as if positive:
    >>> make_block_numbers(1000, 0, -9999, 0)
    (1000, -9999)

    None is ignored, but at least one number must be provided:

    >>> make_block_numbers(None, None, None, None)
    Traceback (most recent call last):
    ...
    ValueError: No non-None addresses provided

    >>> make_block_numbers(None, None, None, 1)
    (1, 1)

    Handles strings that look like integers too. Note that they
    are returned unchanged:

    >>> make_block_numbers('1000', '0', u'9999', u'')
    ('1000', u'9999')

    It also, *for sorting purposes*, tries to ignore any non-numeric
    characters, and if one looks like an address range (like "10-20"),
    it compares only the absolute value of the first numeric part -
    but again, returns them unchanged.  For example, this sorts them
    as if they were 99 and 33 respectively:

    >>> make_block_numbers('blah 99 blah', '33-44-55', '', '')
    ('33-44-55', 'blah 99 blah')

    This also sorts them as if they were 33 and 99 (not -99):

    >>> make_block_numbers('33-44-55', '-99-123', '', '')
    ('33-44-55', '-99-123')

    >>> make_block_numbers('a', 'b', 'c', 'd')
    Traceback (most recent call last):
    ...
    ValueError: No non-zero numeric addresses provided in ['a', 'b', 'c', 'd']

    >>> make_block_numbers('a', 'b', 'c', 'd9d')
    ('d9d', 'd9d')
    """
    nums = [x for x in (left_from_num, left_to_num, right_from_num, right_to_num)
            if x not in (None, '', u'')]
    if not nums:
        # This used to raise ValueError, maybe accidentally, because
        # min([]) does so. Preserving that for backward compatibility,
        # not sure if it matters.
        raise ValueError("No non-None addresses provided")
    # Note that we may get passed strings with non-numeric junk.
    # In that case, try to grab out the numbers for sorting.
    sortable = []
    for x in nums:
        if isinstance(x, basestring):
            maybe = re.search('(\d+)', x)
            if maybe:
                sortkey = int(maybe.group(1))
                if sortkey:
                    sortable.append((sortkey, x))
        else:
            if x:
                sortable.append((abs(x), x))
    if sortable:
        sortable.sort()
        return (sortable[0][1], sortable[-1][1])
    else:
        raise ValueError("No non-zero numeric addresses provided in %s" % nums)


def make_pretty_directional(directional):
    """
    Returns a formatted directional.

    e.g.:

        N -> N.
        NW -> N.W.
    """
    return "".join(u"%s." % c for c in directional)

def make_pretty_name(left_from_num, left_to_num, right_from_num, right_to_num, predir, street, suffix, postdir=None):
    """
    Returns a tuple of (street_pretty_name, block_pretty_name) for the
    given address bits.
    """
    street_name = make_street_pretty_name(street, suffix)
    num_part = make_block_number(left_from_num, left_to_num, right_from_num, right_to_num)
    predir_part = predir and make_pretty_directional(predir) or u''
    postdir_part = postdir and make_pretty_directional(postdir) or u''
    block_name = u'%s %s %s %s' % (num_part, predir_part, street_name, postdir_part)
    block_name = re.sub(u'\s+', u' ', block_name).strip()
    return street_name, block_name

def make_dir_street_name(block):
    """
    Returns a street name from a block with the directional included.

    If the block has a ``predir``, the directional is prepended:

        "W. Diversey Ave."

    If the block has a ``postdir``, the directional is appended:

        "18th St. N.W."
    """
    name = make_street_pretty_name(block.street, block.suffix)
    if block.predir:
        name = u"%s %s" % (make_pretty_directional(block.predir), name)
    if block.postdir:
        name = u"%s %s" % (name, make_pretty_directional(block.postdir))
    return name

def pretty_name_from_blocks(block_a, block_b):
    return u"%s & %s" % (make_dir_street_name(block_a), make_dir_street_name(block_b))

def slug_from_blocks(block_a, block_b):
    slug = u"%s-and-%s" % (slugify(make_dir_street_name(block_a)),
                           slugify(make_dir_street_name(block_b)))
    # If it's too long for the slug field, drop the directionals
    if len(slug) > 64:
        slug = u"%s-and-%s" % (slugify(make_street_pretty_name(block_a.street, block_a.suffix)),
                               slugify(make_street_pretty_name(block_b.street, block_b.suffix)))
    # If it's still too long, drop the suffixes
    if len(slug) > 64:
        slug = u"%s-and-%s" % (slugify(block_a.street),
                               slugify(block_b.street))

    return slug

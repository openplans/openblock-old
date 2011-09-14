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

# The number of days to use in sparklines.
# A sparkline, in this context, is the aggregate view of
# how many NewsItems were added per page.
NUM_DAYS_AGGREGATE = 30

# A timedelta that can be added to an end date to get a start date
# that gives NUM_DAYS_AGGREGATE days total, *inclusive*.
# This was hardcoded in a few places, leading to several mismatches
# between expected date ranges.
import datetime
DAYS_AGGREGATE_TIMEDELTA = datetime.timedelta(days=NUM_DAYS_AGGREGATE - 1)

# A shorter span for use where there's not so much room,
# eg. in the ajax views used by place_detail_overview.
NUM_DAYS_SHORT_AGGREGATE = 10
DAYS_SHORT_AGGREGATE_TIMEDELTA = datetime.timedelta(days=NUM_DAYS_SHORT_AGGREGATE-1)

# Number of results per page in the schema_filter view.
FILTER_PER_PAGE = 30

# Number of NewsItems to fetch for place_detail.
NUM_NEWS_ITEMS_PLACE_DETAIL = 300

# Regular expression that parses block-page URLs. The last part of it is for
# the optional pre-directional and/or post-directional (for example,
# 'n', 'ne', 'n-w', '-sw').
BLOCK_URL_REGEX = r'(\d{1,6})-(\d{1,6})([nsew]{1,2})?(?:-([nsew]{0,2}))?'

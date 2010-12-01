# The number of days to use in sparklines.
# A sparkline, in this context, is the aggregate view of
# how many NewsItems were added per page.
NUM_DAYS_AGGREGATE = 30

# Number of results per page in the schema_filter view.
FILTER_PER_PAGE = 30

# Number of NewsItems to fetch for place_detail.
# Gotcha/caveat: If there are more than this number of items in a given day,
# then place_detail will ignore the day because of the smart_bunches()
# logic.
NUM_NEWS_ITEMS_PLACE_DETAIL = 300

# Regular expression that parses block-page URLs. The last part of it is for
# the optional pre-directional and/or post-directional (for example,
# 'n', 'ne', 'n-w', '-sw').
BLOCK_URL_REGEX = r'(\d{1,6})-(\d{1,6})([nsew]{1,2})?(?:-([nsew]{1,2}))?'

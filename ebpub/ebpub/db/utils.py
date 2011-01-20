from django.conf import settings
import datetime

def smart_bunches(newsitem_list, max_days=5, max_items_per_day=100):
    """
    Helper function that takes a list of NewsItems, ordered descending by
    pub_date, and returns a list of NewsItems that's been optimized for
    display in timelines.

    Assumes each NewsItem has a pub_date_date attribute!

    The logic is:
        * Go backwards in time until there are 5 full days' worth of news
          (not necessarily 5 consecutive days).
        * If, for any day, there are more than 100 items, stop at that day
          (inclusive).
        * Any NewsItems in the list with a pub_date equal to the oldest
          pub_date in the list will be removed. This is because we cannot
          assume *all* of the items with that pub_date are in the list.
    """
    if newsitem_list:
        current_date = None
        days_seen = 0
        stop_at_next_day = False
        end_index = None
        oldest_pub_date = newsitem_list[-1].pub_date_date
        for i, ni in enumerate(newsitem_list):
            if ni.pub_date_date != current_date:
                days_seen += 1
                current_date = ni.pub_date_date
                items_in_current_day = 1
                if stop_at_next_day or days_seen > max_days or ni.pub_date_date == oldest_pub_date:
                    end_index = i
                    break
            else:
                items_in_current_day += 1
                if items_in_current_day > max_items_per_day:
                    stop_at_next_day = True
        if end_index is not None:
            del newsitem_list[end_index:]
    return newsitem_list

def convert_to_spike_models(newsitem_list):
    """
    Given a list of vanilla NewsItems, this converts them
    to subclasses based on the schema of each.
    """
    # XXX this is badly inefficient, makes a hit to the db for EACH
    # newsitem: a join against db_newsitem and the extra model table.

    # XXX move this somewhere more sensible, like NewsItemQuerySet?
    # XXX ... or, since populate_attributes_if_needed() is already done
    # anywhere we would need this, rewrite it to do something
    # semi-sensible (maybe N queries where N = number of model subclasses)
    # and mutate ni_list in-place?
    results = []
    for ni in newsitem_list:
        if ni.schema.slug == 'issues':
            new_ni = ni.seeclickfixissue
        elif ni.schema.slug == 'restaurant-inspections':
            new_ni = ni.restaurantinspection
        else:
            new_ni = ni
        if hasattr(ni, '_schema_cache'):
            new_ni._schema_cache = ni._schema_cache
        results.append(ni)
    return results

def populate_attributes_if_needed(newsitem_list, schema_list):
    """
    Helper function that takes a list of NewsItems and sets ni.attribute_values
    to a dictionary of attributes {field_name: value} for all NewsItems whose
    schemas have uses_attributes_in_list=True. This is accomplished with a
    minimal amount of database queries.

    The values in the attribute_values dictionary are Lookup instances in the
    case of Lookup fields. Otherwise, they're the direct values from the
    Attribute table.

    schema_list should be a list of all Schemas that are referenced in
    newsitem_list.

    Note that the list is edited in place; there is no return value.
    """
    # XXX in the datamodel-spike branch, this no longer does anything,
    # since all our newsitems are presumably already approprate subclasses.
    return


def populate_schema(newsitem_list, schema):
    for ni in newsitem_list:
        # TODO: This relies on undocumented Django APIs -- the "_schema_cache" name.
        ni._schema_cache = schema

def today():
    if settings.EB_TODAY_OVERRIDE:
        return settings.EB_TODAY_OVERRIDE
    return datetime.date.today()

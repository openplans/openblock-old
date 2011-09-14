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

from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from ebpub.alerts.models import EmailAlert
from ebpub.db.models import NewsItem
from ebpub.db.utils import populate_attributes_if_needed
from ebpub.db.utils import make_search_buffer
from ebpub.streets.models import Block
import datetime

class NoNews(Exception):
    pass

def email_text_for_place(alert, place, place_name, place_url,
                         news_groups, date, frequency):
    """
    Returns a tuple of (text, html) for the given args. `text` is the text-only
    e-mail, and `html` is the HTML version.
    """
    domain = settings.EB_DOMAIN
    context = {
        'place': place,
        'is_block': isinstance(place, Block),
        'block_radius': isinstance(place, Block) and alert.radius or None,
        'domain': domain,
        'email_address': alert.user.email,
        'place_name': place_name,
        'place_url': place_url,
        'news_groups': news_groups,
        'date': date,
        'frequency': frequency,
        'unsubscribe_url': alert.unsubscribe_url(),
    }
    return render_to_string('alerts/email.txt', context), render_to_string('alerts/email.html', context)

def email_for_subscription(alert, start_date, frequency):
    """
    Returns a (place_name, text, html) tuple for the given EmailAlert
    object and date.
    """
    start_datetime = datetime.datetime(start_date.year, start_date.month, start_date.day)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    end_datetime = datetime.datetime.combine(yesterday, datetime.time(23, 59, 59, 9999)) # the end of yesterday
    # Order by schema__id to group schemas together.
    qs = NewsItem.objects.select_related().filter(schema__is_public=True)
    if alert.include_new_schemas:
        if alert.schemas:
            qs = qs.exclude(schema__id__in=alert.schemas.split(','))
    else:
        if alert.schemas:
            qs = qs.filter(schema__id__in=alert.schemas.split(','))

    if alert.block:
        place_name, place_url = alert.block.pretty_name, alert.block.url()
        place = alert.block
        search_buffer = make_search_buffer(alert.block.location.centroid, alert.radius)
        qs = qs.filter(location__bboverlaps=search_buffer)
    elif alert.location:
        place_name, place_url = alert.location.name, alert.location.url()
        place = alert.location
        qs = qs.filter(newsitemlocation__location__id=alert.location.id)

    news_qs = qs.filter(schema__is_event=False,
                        pub_date__range=(start_datetime, end_datetime),
                        ).order_by('-schema__importance', 'schema__id', '-item_date', '-id')
    events_qs = qs.filter(schema__is_event=True,
                         pub_date__range=(start_datetime, end_datetime),
                         ).order_by('-schema__importance', 'schema__id', 'item_date', 'id')

    news_list = list(news_qs)
    events_list = list(events_qs)
    if not (news_list or events_list):
        raise NoNews
    schemas_used = set([ni.schema for ni in news_list + events_list])
    populate_attributes_if_needed(news_list, list(schemas_used))
    populate_attributes_if_needed(events_list, list(schemas_used))
    newsitem_groups = ({'title': 'Recent', 'newsitems': news_list},
                       {'title': 'Upcoming', 'newsitems': events_list})
    text, html = email_text_for_place(alert, place, place_name, place_url, newsitem_groups, start_date, frequency)
    return place_name, text, html

def send_all(frequency, verbose=False):
    """
    Sends an e-mail to all alert subscribers in the system with data
    with the given frequency (in days).

    Note that it does not keep track of already-sent messages, so take
    care not to call send_all(frequency) more often than ``frequency`` days.
    """
    conn = get_connection() # Use default settings.
    count = 0
    start_date = datetime.date.today() - datetime.timedelta(days=frequency)
    for alert in EmailAlert.active_objects.filter(frequency=frequency):
        try:
            place_name, text_content, html_content = email_for_subscription(alert, start_date, frequency)
        except NoNews:
            continue
        subject = 'Update: %s' % place_name
        message = EmailMultiAlternatives(subject, text_content, settings.GENERIC_EMAIL_SENDER,
            [alert.user.email], connection=conn)
        message.attach_alternative(html_content, 'text/html')
        message.send()
        if verbose:
            print "Sent to %s" % alert.user.email
        count += 1
    return count

def main(argv=None):
    if argv is None:
        import sys
        argv = sys.argv[1:]
    from optparse import OptionParser
    freq_choices = {'daily': 1, 'weekly': 7}
    usage = """usage: %prog [options]\nSends OpenBlock email alerts.

Warning, the system does not keep track of which alerts you've already sent.
Eg. you should run this script with --frequency='daily' exactly once per day,
NOT more, or you will send duplicate email.
"""
    optparser = OptionParser(usage=usage)
    optparser.add_option('-f', '--frequency', type="choice",
                         choices=freq_choices.keys(),
                         help='Which email alerts to send (choices: %s)' % ', '.join(freq_choices.keys()))
    optparser.add_option('-v', '--verbose', action='store_true')
    opts, args = optparser.parse_args(argv)
    try:
        frequency = freq_choices[opts.frequency]
    except KeyError:
        sys.stderr.write("Error: You must choose a valid frequency.\n\n")
        optparser.print_help()
        return 1
    count = send_all(frequency, opts.verbose)
    print "Sent %d messages for %s subscriptions" % (count, opts.frequency)


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
Management utility to create superusers for OpenBlock,
with email address instead of username.

In order for this to override the default createsuperuser command,
ebpub.accounts needs to be in INSTALLED_APPS later than
django.contrib.*.
"""

import getpass
import os
import re
import sys
from optparse import make_option
from ebpub.accounts.models import User
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

EMAIL_RE = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain

def is_valid_email(value):
    if not EMAIL_RE.search(value):
        raise exceptions.ValidationError(_('Enter a valid e-mail address.'))

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--email', dest='email', default=None,
            help='Specifies the email address for the superuser.'),
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind. '    \
                 'You must use --email with --noinput, and '      \
                 'superusers created with --noinput will not be able to log in '  \
                 'until they\'re given a valid password.'),
    )
    help = 'Used to create a superuser.'

    def handle(self, *args, **options):
        email = options.get('email', None)
        interactive = options.get('interactive')
        
        # Do quick and dirty validation if --noinput
        if not interactive:
            if not email:
                raise CommandError("You must use --email with --noinput.")
            try:
                is_valid_email(email)
            except exceptions.ValidationError:
                raise CommandError("Invalid email address.")

        password = ''

        # Prompt for username/email/password. Enclose this whole thing in a
        # try/except to trap for a keyboard interrupt and exit gracefully.
        if interactive:
            try:
                # Get an email
                while 1:
                    if not email:
                        email = raw_input('E-mail address: ')
                    try:
                        is_valid_email(email)
                        try:
                            User.objects.get(email=email)
                        except User.DoesNotExist:
                            break
                        else:
                            sys.stderr.write("Error: That email address is already taken.\n")
                            email = None

                    except exceptions.ValidationError:
                        sys.stderr.write("Error: That e-mail address is invalid.\n")
                        email = None
                    else:
                        break

                # Get a password
                while 1:
                    if not password:
                        password = getpass.getpass()
                        password2 = getpass.getpass('Password (again): ')
                        if password != password2:
                            sys.stderr.write("Error: Your passwords didn't match.\n")
                            password = None
                            continue
                    if password.strip() == '':
                        sys.stderr.write("Error: Blank passwords aren't allowed.\n")
                        password = None
                        continue
                    break
            except KeyboardInterrupt:
                sys.stderr.write("\nOperation cancelled.\n")
                sys.exit(1)
        
        User.objects.create_superuser(email, password)
        print "Superuser created successfully."

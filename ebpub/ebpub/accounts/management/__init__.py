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
Signals to defer creating a superuser until all the necessary models
exist, since we can't create user accounts without both ebpub.accounts
and ebpub.preferences models in the database.
"""

from django.db.models import signals as django_signals
from south import signals as south_signals
from django.contrib.auth import models as auth_app

_state = {'created_apps': set(), 'interactive': True, 'superuser_created': False}

def should_create_superuser():
    return ((not _state['superuser_created'])
            and'auth' in _state['created_apps']
            and 'accounts' in _state['created_apps']
            and 'preferences' in _state['created_apps']
            and _state['interactive']
            )

def probably_dont_create_superuser(app, created_models, verbosity, **kwargs):
    from django.contrib.auth.models import User
    _state['interactive'] = kwargs.get('interactive', True)
    if User in created_models:
        _state['created_apps'].add('auth')
    # TODO: Somehow detect if preferences and accounts models already exist,
    # just in case we ever stop using South for ebpub.preferences
    # and/or ebpub.accounts.
    if should_create_superuser():
        _create_superuser()

def maybe_now_create_superuser(*args, **kwargs):
    app = kwargs.get('app')
    _state['created_apps'].add(app)
    if should_create_superuser():
        _create_superuser()

def _create_superuser():
    from django.core.management import call_command
    msg = "\nYou just installed Django's auth system, which means you don't have " \
            "any superusers defined.\nWould you like to create one now? (yes/no): "
    while True:
        confirm = raw_input(msg).strip().lower()
        if confirm not in ('yes', 'no'):
            msg = 'Please enter either "yes" or "no": '
            continue
        if confirm == 'yes':
            call_command("createsuperuser", interactive=True)
            _state['superuser_created'] = True
        break

# Unregister the default handler that creates superusers too early for us.
django_signals.post_syncdb.disconnect(
    sender=auth_app, dispatch_uid="django.contrib.auth.management.create_superuser")

# Block it from being re-registered by registering our handler in its place.
django_signals.post_syncdb.connect(probably_dont_create_superuser,
    sender=auth_app, dispatch_uid="django.contrib.auth.management.create_superuser")

# Register our handler to run after everything's ready.
south_signals.post_migrate.connect(maybe_now_create_superuser)

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

from django.db.models import signals as django_signals
from south import signals as south_signals
from django.contrib.auth import models as auth_app
from django.contrib.auth.management import create_superuser


should_create_superuser = False

def dont_create_superuser(app, created_models, verbosity, **kwargs):
    from django.contrib.auth.models import User
    global should_create_superuser
    if User in created_models and kwargs.get('interactive', True):
        should_create_superuser = True
    else: 
        should_create_superuser = False

def okay_now_create_superuser(*args, **kwargs):
    global should_create_superuser
    if kwargs.get('app') == 'accounts' and should_create_superuser:
        from django.core.management import call_command
        msg = "\nYou just installed Django's auth system, which means you don't have " \
                "any superusers defined.\nWould you like to create one now? (yes/no): "
        confirm = raw_input(msg)
        while 1:
            if confirm not in ('yes', 'no'):
                confirm = raw_input('Please enter either "yes" or "no": ')
                continue
            if confirm == 'yes':
                call_command("createsuperuser", interactive=True)
            break

# we need the accounts tables to be migrated in before we can use our 
# superusercommand. 
django_signals.post_syncdb.disconnect(sender=auth_app, dispatch_uid = "django.contrib.auth.management.create_superuser")
# block it from being re-registered by registering somehting in its place
django_signals.post_syncdb.connect(dont_create_superuser,
    sender=auth_app, dispatch_uid = "django.contrib.auth.management.create_superuser")
    
# instead, we'll call it after the account's app has been migrated
south_signals.post_migrate.connect(okay_now_create_superuser)

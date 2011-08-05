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

import datetime
from django.db import models
from django.contrib.auth.models import User as DjangoUser, UserManager as DjangoUserManager, AnonymousUser
from django.contrib.auth.backends import ModelBackend
from django.utils.hashcompat import md5_constructor

class UserManager(DjangoUserManager):

    def create_user(self, email, password=None, **kw):
        """
        Creates and saves a User with the given e-mail and password.
        """

        now = datetime.datetime.now()
        
        # Normalize the address by lowercasing the domain part of the email
        # address.
        try:
            email_name, domain_part = email.strip().split('@', 1)
        except ValueError:
            first_name = email[0:30]
        else:
            email = '@'.join([email_name, domain_part.lower()])
            first_name = email_name

        # something of a hack...
        # the username is used to enforce uniqueness and is computed
        # as a (truncated) hash of the email address given.
        if len(email) <= 30:
            username = email
        else:
            username = md5_constructor(email).hexdigest()[0:30]
        
        user_args = dict(
            first_name=first_name,
            is_staff=False,
            is_active=True, 
            is_superuser=False,
            last_login=now,
            date_joined=now
        )
        user_args.update(kw)
        user = User(username=username, email=email, **user_args)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kw):
        user_args = dict(kw)
        user_args['is_superuser'] = True
        user_args['is_staff'] = True
        return self.create_user(email, password=password, **user_args)

    def user_by_password(self, email, raw_password):
        """
        Returns a User object for the given e-mail and raw password. If the
        e-mail address exists but the password is incorrect, returns None.
        """
        try:
            user = self.get(email=email)
        except self.model.DoesNotExist:
            return None
        if user.check_password(raw_password):
            return user
        return None

class User(DjangoUser):
    """ A very thin multi-table-inheritance wrapper around the default User class.
    """

    main_metro = models.CharField(
        max_length=32,
        help_text="The SHORT_NAME for the user's metro when they created the account. Only useful if you have multiple metros.")

    objects = UserManager()

    def __unicode__(self):
        return self.email

class AuthBackend(ModelBackend):

    def authenticate(self, username=None, password=None):
        return User.objects.user_by_password(username, password)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

# Note that this class does *not* use the multidb Manager.
# It's city-specific because pending user actions are city-specific.

class PendingUserAction(models.Model):
    email = models.EmailField(db_index=True) # Stored in all-lowercase.
    callback = models.CharField(max_length=50)
    data = models.TextField() # Serialized into JSON.
    action_date = models.DateTimeField() # When the action was created (so we can clear out expired ones).

    def __unicode__(self):
        return u'%s for %s' % (self.callback, self.email)


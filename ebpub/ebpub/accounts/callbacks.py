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

# This is a lightweight framework for passing events that need to happen
# when users log in successfully. For example, there's a way to specify that
# an e-mail alert should be created for a given user as soon as he logs in.

from django.utils import simplejson
from ebpub.alerts.models import EmailAlert
import datetime

###############
# SERIALIZING #
###############

# We store compressed JSON in the PendingUserAction table.

def serialize(data):
    return simplejson.dumps(data)

def unserialize(data):
    return simplejson.loads(data)

#############
# CALLBACKS #
#############

def do_callback(callback_name, user, data):
    # callback_name is a key in CALLBACKS.
    # serialized_data is an unserialized Python object.
    try:
        callback = CALLBACKS[callback_name]
    except KeyError:
        return None
    return callback(user, data)

def create_alert(user, data):
    EmailAlert.objects.create(
        user_id=user.id,
        block_id=data['block_id'],
        location_id=data['location_id'],
        frequency=data['frequency'],
        radius=data['radius'],
        include_new_schemas=data['include_new_schemas'],
        schemas=data['schemas'],
        signup_date=datetime.datetime.now(),
        cancel_date=None,
        is_active=True,
    )
    return "Your e-mail alert was created successfully. Thanks for signing up!"

CALLBACKS = {
    'createalert': create_alert,
}

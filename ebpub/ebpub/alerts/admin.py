#   Copyright 2012 OpenPlans and contributors
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

from .models import EmailAlert
from ebpub.geoadmin import OSMModelAdmin
from django.contrib.gis import admin


class AlertAdmin(OSMModelAdmin):

    readonly_fields = ('block',)

    # TODO: need to refactor the BlockAlertForm clean() method so we
    # can use it here too... and the extra form fields that it needs.
    # Otherwise we can't save with empty schema list.


admin.site.register(EmailAlert, AlertAdmin)

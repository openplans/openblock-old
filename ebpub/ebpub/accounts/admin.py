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

from django.contrib import admin
from ebpub.accounts.models import User
from ebpub.geoadmin import OSMModelAdmin
from ebpub.preferences.models import Profile
from ebpub.openblockapi.apikey.admin import ApiKeyForm, ApiKey

class ProfileInline(admin.StackedInline):
    model = Profile
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = 'Profile'

class ApiKeyInline(admin.StackedInline):
    model = ApiKey
    form = ApiKeyForm
    fk_name = 'user'
    extra = 0

class UserAdmin(OSMModelAdmin):
    inlines = [
        ApiKeyInline,
        ProfileInline,
        ]

admin.site.register(User, UserAdmin)

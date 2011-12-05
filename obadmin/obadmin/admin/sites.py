#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#

from django.contrib.admin import AdminSite
import ebpub.accounts.forms

class OpenblockAdminSite(AdminSite):
    """
    A custom AdminSite.

    This admin site specialized to use the openblock login methods
    instead of the django.contrib.auth methods.
    """

    login_form = ebpub.accounts.forms.AdminLoginForm
    login_template = 'accounts/login_form.html'

    logout_template = 'accounts/logout_form.html'

    def get_urls(self):
        """
        Add some extra URLs to the admin site, as per
        https://docs.djangoproject.com/en/dev/ref/contrib/admin/#adding-views-to-admin-sites
        """
        from obadmin.admin.urls import urlpatterns as local_urls

        url_patterns = local_urls
        url_patterns += AdminSite.get_urls(self)

        return url_patterns

site = OpenblockAdminSite()

def autodiscover():
    global site
    # workaround the somewhat short-sighted admin registry convention
    # by copying the global admin site's registry after autodiscover,
    # because our ModelAdmins got registered with the global admin site.
    from copy import copy
    from django.contrib import admin
    admin.autodiscover()
    site._registry = copy(admin.site._registry)

    # unregister the django.contrib.auth.models, openblock
    # uses specialized versions.
    from django.contrib.auth.models import User, Group
    site.unregister([User, Group])

    # Also, our registered ModelAdmin instances have a reference to
    # the default admin site.  This has implications for eg. the admin
    # site login form, which is looked up via that reference.  Patch
    # those so we get the right login form. Sigh.
    for admin_instance in site._registry.values():
        admin_instance.admin_site = site

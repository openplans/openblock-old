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
from django.views.decorators.cache import never_cache

class OpenblockAdminSite(AdminSite):
    """
    A custom AdminSite for using 
    
    This admin site specialized to use
    the openblock login methods instead of the 
    django.contrib.auth methods.
    """
    
    def logout(self, request):
        from ebpub.accounts.views import logout
        return logout(request)
    logout = never_cache(logout)

    def login(self, request):
        """
        Displays the login form
        """
        from ebpub.accounts.views import login
        request.session['next_url'] = request.get_full_path()
        return login(request)
    login = never_cache(login)
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include
        from obadmin.admin.urls import urlpatterns as local_urls

        url_patterns = local_urls
        url_patterns += AdminSite.get_urls(self)

        return url_patterns

site = OpenblockAdminSite()

def autodiscover():
    global site
    # workaround the somewhat short-sighted admin registry convention 
    # by stealing the global admin site's registry after autodiscover
    from copy import copy
    from django.contrib import admin
    admin.autodiscover()
    site._registry = copy(admin.site._registry)
    
    # unregister the django.contrib.auth.models, openblock
    # uses specialized versions.
    from django.contrib.auth.models import User, Group
    site.unregister([User, Group])
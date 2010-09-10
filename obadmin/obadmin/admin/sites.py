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
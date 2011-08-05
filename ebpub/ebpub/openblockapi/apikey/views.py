"""
Views for managing REST API keys.

Derived from django-apikey,
copyright (c) 2011 Steve Scoursen and Jorge Eduardo Cardona.
BSD license.
http://pypi.python.org/pypi/django-apikey
"""

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import condition
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import ApiKey, generate_unique_api_key
import datetime


def get_etag_key(request):
    try:
        lm = request.user.get_profile().last_accessed
    except:
        try:
            lm = request.get_profile().last_accessed
        except:
            lm = datetime.datetime.utcnow()
    k = 'etag.%s' % (lm)
    return k.replace(' ', '_')

def etag_func(request, *args, **kwargs):
    etag_key = get_etag_key(request)
    etag = cache.get(etag_key, None)
    return etag

def latest_access(request, *args, **kwargs):
    try:
        return request.user.get_profile().last_accessed
    except:
        return datetime.datetime.utcnow()



@login_required
@condition(etag_func=etag_func, last_modified_func=latest_access)
@cache_page(1)
def generate_key(request):
    if request.method == 'POST':
        # Trigger loading the real user object (not a LazyUser proxy),
        # and use it.
        user = request.user.user
        key = generate_unique_api_key()
        apikey = ApiKey(user=user, key=key)
        apikey.clean()
        apikey.save()
    return do_generate_key_list(request)


@login_required
@condition(etag_func=etag_func, last_modified_func=latest_access)
@cache_page(1)
def list_keys(request):
    return do_generate_key_list(request)

def do_generate_key_list(request):
    # Trigger loading the real user object (not a LazyUser proxy),
    # and use it.
    user = request.user.user
    profile = user.get_profile()
    keys = ApiKey.objects.filter(user=user)
    cmak = profile.can_make_api_key()
    ak = profile.available_keys()
    return render_to_response('key/key.html',
                              { 'keys': keys, 'user': user,
                                'can_make_api_key': cmak,
                                'available_keys': ak },
                              context_instance=RequestContext(request))

@login_required
@condition(etag_func=etag_func, last_modified_func=latest_access)
@cache_page(1)
def delete_key(request):
    user = request.user.user
    keys = ApiKey.objects.filter(user=user)
    return render_to_response('key/key.html',
                              { 'keys': keys,
                                'user': user },
                              context_instance=RequestContext(request))

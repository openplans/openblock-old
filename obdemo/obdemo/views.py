"""
Views for openblock demo.

If these turn out to be really useful they could be merged upstream
into ebpub.
"""
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext



def geotagger_ui(request): 
    return render_to_response('geotagger/geotagger.html', RequestContext(request, {}))

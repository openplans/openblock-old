"""
obdemo-specific stuff we might need in templates.
"""

from django.conf import settings

def urls(request):
    return {'OPENLAYERS_URL': settings.OPENLAYERS_URL}

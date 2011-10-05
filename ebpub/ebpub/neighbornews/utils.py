from django.http import HttpResponse
from ebpub.db.models import Schema

NEIGHBOR_MESSAGE_SLUG = 'neighbor-messages'
NEIGHBOR_EVENT_SLUG = 'neighbor-events'


def app_enabled():
    from django.conf import settings
    return 'ebpub.neighbornews' in settings.INSTALLED_APPS

def is_schema_enabled(slug):
    try: 
        return app_enabled() and Schema.objects.filter(slug=slug).values_list('is_public')[0][0]
    except IndexError:
        return False

def is_neighbor_message_enabled():
    return is_schema_enabled(NEIGHBOR_MESSAGE_SLUG)
    
def is_neighbor_event_enabled():
    return is_schema_enabled(NEIGHBOR_EVENT_SLUG)

def is_neighbornews_enabled():
    """
    check if the neighbornews schemas exist and are 
    enabled.
    """
    return is_neighbor_message_enabled() or is_neighbor_event_enabled()

def if_disabled404(slug):
    def decorator(func):
        def inner(*args, **kw):
            if not is_schema_enabled(slug): 
                return HttpResponse(status=404)
            else: 
                return func(*args, **kw)
        return inner
    return decorator

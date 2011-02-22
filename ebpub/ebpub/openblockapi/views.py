from django.http import HttpResponse

def check_api_available(request):
    """
    endpoint to indicate that this version of the API
    is available.
    """
    return HttpResponse(status=200)

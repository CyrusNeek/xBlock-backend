from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    """
    A simple health check endpoint that returns 200 OK if the application is running.
    """
    return HttpResponse("OK", content_type="text/plain") 
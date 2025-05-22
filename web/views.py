from django.http import HttpResponse

def index(request):
    return HttpResponse("Web app is running", content_type="text/plain")

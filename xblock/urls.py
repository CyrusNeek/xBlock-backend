"""xblock URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def health_check(request):
    """Simple health check endpoint for Cloud Run"""
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', health_check, name='health_check'),
    path('', health_check, name='root_health_check'),  # Root path for health check
    path('web/', include('web.urls')),
]

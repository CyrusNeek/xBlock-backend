"""xblock URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request):
    """API root view showing available endpoints"""
    return Response({
        'admin': reverse('admin:index', request=request),
        'health': reverse('health_check', request=request),
        'api': reverse('api-root', request=request),
        'docs': '/api/schema/swagger-ui/',
    })

def health_check(request):
    """Simple health check endpoint for Cloud Run"""
    return JsonResponse({"status": "OK", "message": "xBlock API is running"}, status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', health_check, name='health_check'),
    path('', api_root, name='root'),
    path('api/', include('web.urls')),
]

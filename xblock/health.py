import os
import sys
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError

@csrf_exempt
def health_check(request):
    """
    A health check endpoint that verifies the application is running correctly.
    Checks:
    - Basic application status
    - Database connectivity
    - Static files directory
    - Media files directory
    """
    try:
        # Check database connectivity
        db_conn = connections['default']
        db_conn.cursor()
        
        # Check static files directory
        if not os.path.exists(settings.STATIC_ROOT):
            return HttpResponse("Static files directory not found", status=500)
            
        # Check media files directory
        if not os.path.exists(settings.MEDIA_ROOT):
            return HttpResponse("Media files directory not found", status=500)
            
        # All checks passed
        return HttpResponse("OK", content_type="text/plain")
        
    except OperationalError:
        return HttpResponse("Database connection failed", status=500)
    except Exception as e:
        return HttpResponse(f"Health check failed: {str(e)}", status=500) 
from django.http import JsonResponse
from django.views import View
from django.db import connections
from django.db.utils import OperationalError

class HealthCheckView(View):
    """Health check endpoint for Cloud Run."""
    
    def get(self, request, *args, **kwargs):
        try:
            # Try to connect to all databases
            for conn in connections.all():
                conn.ensure_connection()
                conn.close()
            
            return JsonResponse({
                "status": "healthy",
                "message": "Service is running and database connections are working"
            })
        except OperationalError as e:
            return JsonResponse({
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }, status=503)
        except Exception as e:
            return JsonResponse({
                "status": "unhealthy",
                "message": f"Service check failed: {str(e)}"
            }, status=503)

from constance import config
from django.http import HttpResponse
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def cors_whitelist_extra_from_constance():
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Fetch and process the extra allowed origins from Constance config
            allowed_origins_extra = config.CORS_ALLOWED_ORIGINS_EXTRA.split(',')
            logging.info(f'Allowed origins extra: {allowed_origins_extra}')

            response = view_func(request, *args, **kwargs)
            origin = request.META.get('HTTP_ORIGIN', '')

            # Check against the extra whitelist
            if origin and origin.strip() in allowed_origins_extra:
                logging.info(f'Allowed origin: {origin}$$$$')
                
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type'
            
            return response
        return _wrapped_view
    return decorator

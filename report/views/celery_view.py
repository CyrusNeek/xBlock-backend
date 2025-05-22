from django.http import JsonResponse
from celery import Celery

# Assuming your app is named 'xblock'
app = Celery('xblock')

def celery_queues(request):
    # Inspect the Celery workers
    try:
        inspect = app.control.inspect()
        queues = inspect.active_queues()
    except Exception as e:
        print("e", e)
        return JsonResponse({}, safe=False)
    # Return the result as JSON
    return JsonResponse(queues, safe=False)

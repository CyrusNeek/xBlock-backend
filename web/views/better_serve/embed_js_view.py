from django.http import HttpResponse
from django.conf import settings
import os

# View function to serve the JS file

def serve_chat_interface_js(request):
    # Construct the path to the JS file
    js_file_path = os.path.join(settings.BASE_DIR, 'web', 'views', 'better_serve', 'chat-interface.js')
    
    # Open the file for reading
    with open(js_file_path, 'r') as file:
        js_content = file.read()
    
    # Return the JavaScript content with the appropriate MIME type
    return HttpResponse(js_content, content_type='application/javascript')
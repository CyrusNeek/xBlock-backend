from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from google_auth_oauthlib.flow import Flow
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
from datetime import timedelta
import os
import json

SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/tasks"]

class GoogleOAuth2CallbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state = request.session.get('state')

        if not state:
            return HttpResponse("Error: State not found in session.", status=400)

        # Path to the Google credentials JSON file
        current_file_path = os.path.abspath(__file__)
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
        credentials_path = os.path.join(app_path, "google_credentials.json")

        # Initialize the flow with the state and credentials path
        flow = Flow.from_client_secrets_file(
            credentials_path,
            scopes=SCOPES,
            state=state,
            redirect_uri=settings.GOOGLE_OATH_CALLBACK_URL
        )

        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials

        # Store the credentials in Redis cache
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat(),
        }

        cache.set(f"google_oauth_token_{request.user.id}", json.dumps(token_data), timeout=timedelta(days=7))

        return HttpResponse("Authentication successful! You can close this window.")
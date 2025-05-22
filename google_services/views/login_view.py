from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from google_auth_oauthlib.flow import Flow
import os


SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/tasks"]

class GoogleLoginView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Path to the Google credentials JSON file
        current_file_path = os.path.abspath(__file__)
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
        credentials_path = os.path.join(app_path, "google_credentials.json")

        # Create the flow using the client secrets file from the credentials.json file
        flow = Flow.from_client_secrets_file(
            credentials_path,
            scopes=SCOPES,
            redirect_uri='http://beta.xblock.ai/api/google/oauth2callback'
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        # Store the state in the session for later use in the callback
        request.session['state'] = state

        # Redirect the user to the Google authorization URL
        return redirect(authorization_url)
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def get_integration_service_account_token():
    import os
    import json

    # Get credentials from environment variable
    integrations_credentials_json = os.getenv('INTEGRATIONS_CREDENTIALS')
    
    if integrations_credentials_json:
        # Use credentials from environment variable
        service_account_info = json.loads(integrations_credentials_json)
        credentials = service_account.IDTokenCredentials.from_service_account_info(
            service_account_info,
            target_audience="https://us-central1-xbrain-422617.cloudfunctions.net/outlook"
        )
    else:
        # Fallback for local development if needed
        json_file_path = os.getenv('INTEGRATIONS_CREDENTIALS_FILE', 'integrations_credential.json')
        credentials = service_account.IDTokenCredentials.from_service_account_file(
            json_file_path,
            target_audience="https://us-central1-xbrain-422617.cloudfunctions.net/outlook"
        )

    request = Request()
    credentials.refresh(request)

    token = credentials.token
    return token 
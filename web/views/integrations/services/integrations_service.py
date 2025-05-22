from google.oauth2 import service_account
from google.auth.transport.requests import Request

def get_integration_service_account_token():

    json_file_path = "integrations_credential.json"

    credentials = service_account.IDTokenCredentials.from_service_account_file(
        json_file_path,
        target_audience="https://us-central1-xbrain-422617.cloudfunctions.net/outlook"
    )

    request = Request()
    credentials.refresh(request)

    token = credentials.token
    return token 
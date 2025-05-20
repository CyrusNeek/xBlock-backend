from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from web.views.integrations.services import get_integration_service_account_token
from web.views.integrations.constants import ONEDRIVE_API_URL

class OneDriveListDirectoryView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, path,  *args, **kwargs):
        user = request.user
        payload = request.data.copy()
        payload["user_id"] = user.id  
        payload["path"] = path 
        token = get_integration_service_account_token()
        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            integration_request = requests.post(
                f"{ONEDRIVE_API_URL}/dir/list",
                json=payload,
                headers=headers,
                timeout=10  
            )

            if integration_request.status_code == 200:
                return Response(integration_request.json(), status=200)
            else:
                return Response(
                    {"error": "Failed to list directories ", "details": integration_request.text},
                    status=integration_request.status_code,
                )
        except requests.RequestException as e:
            return Response({"error": "Request failed", "details": str(e)}, status=500)
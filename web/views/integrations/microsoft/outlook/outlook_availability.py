from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from web.views.integrations.services import get_integration_service_account_token
from web.views.integrations.constants import OUTLOOK_API_URL

class OutlookAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request, *args, **kwargs):
        user = request.user
        payload = request.data.copy()
        payload["user_id"] = user.id  
        token = get_integration_service_account_token()
        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            integration_request = requests.post(
                f"{OUTLOOK_API_URL}/availability",
                json=payload,
                headers=headers,
                timeout=10  
            )

            if integration_request.status_code == 200:
                return Response(integration_request.json(), status=200)
            else:
                return Response(
                    {"error": "Failed to get user availability", "details": integration_request.text},
                    status=integration_request.status_code,
                )
        except requests.RequestException as e:
            return Response({"error": "Request failed", "details": str(e)}, status=500)
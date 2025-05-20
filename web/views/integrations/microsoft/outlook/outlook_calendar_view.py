from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from web.views.integrations.services import get_integration_service_account_token
from web.views.integrations.constants import OUTLOOK_API_URL

class OutlookCalendarView(APIView):
    permission_classes = [IsAuthenticated]


    # ======= create event 
    def post(self, request, *args, **kwargs):
        user = request.user

        payload = request.data.copy()
        payload["user_id"] = user.id  

        token = get_integration_service_account_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            integration_request = requests.post(
                f"{OUTLOOK_API_URL}/calendar/event-create",
                json=payload,
                headers=headers,
                timeout=10
            )

            return Response(integration_request.json(), status=integration_request.status_code)
        except requests.RequestException as e:
            return Response({"error": "Request failed", "details": str(e)}, status=500)
            
    
            
    # ======= Get All Events (GET) =======
    def get(self, request, *args, **kwargs):
        user = request.user

        token = get_integration_service_account_token()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        payload = {
            "user_id" : user.id 
        }

        try:
            integration_request = requests.post(
                f"{OUTLOOK_API_URL}/calendar/events",
                json=payload,
                headers=headers,
                timeout=10
            )

            return Response(integration_request.json(), status=integration_request.status_code)
        except requests.RequestException as e:
            return Response({"error": "Request failed", "details": str(e)}, status=500)
        

class OutlookCalendarDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id, *args, **kwargs):
        user = request.user

        token = get_integration_service_account_token()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        payload = {
            "user_id" : user.id ,
            "event_id" : event_id
        }

        try:
            integration_request = requests.post(
                f"{OUTLOOK_API_URL}/calendar/event-metadata",
                json=payload,
                headers=headers,
                timeout=10
            )

            return Response(integration_request.json(), status=integration_request.status_code)
        except requests.RequestException as e:
            return Response({"error": "Request failed", "details": str(e)}, status=500)


    # ======= update event 
    def patch(self, request,event_id, *args, **kwargs):
        user = request.user

        payload = request.data.copy()
        payload["user_id"] = user.id  
        payload["event_id"] = event_id  

        token = get_integration_service_account_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            integration_request = requests.post(
                f"{OUTLOOK_API_URL}/calendar/event-update",
                json=payload,
                headers=headers,
                timeout=10
            )

            return Response(integration_request.json(), status=integration_request.status_code)
        except requests.RequestException as e:
            return Response({"error": "Request failed", "details": str(e)}, status=500)
   
   
    # ======= delete event 
    def delete(self, request,event_id, *args, **kwargs):
        user = request.user

        payload = request.data.copy()
        payload["user_id"] = user.id  
        payload["event_id"] = event_id  

        token = get_integration_service_account_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            integration_request = requests.post(
                f"{OUTLOOK_API_URL}/calendar/event-delete",
                json=payload,
                headers=headers,
                timeout=10
            )

            return Response(integration_request.json(), status=integration_request.status_code)
        except requests.RequestException as e:
            return Response({"error": "Request failed", "details": str(e)}, status=500)
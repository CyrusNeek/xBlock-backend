import calendar
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.core.cache import cache
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_services.serializers import DateRangeSerializer, EventSerializer, TaskSerializer
from datetime import datetime

def get_credentials(user):
    token_data = cache.get(f"google_oauth_token_{user.id}")
    if not token_data:
        raise NotFound("No credentials found for this user.")
    token_data = json.loads(token_data)
    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data['token'] = creds.token
        token_data['expiry'] = creds.expiry
        cache.set(f"google_oauth_token_{user.id}", json.dumps(token_data), timeout=datetime.timedelta(days=7))
    return creds

class CalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = DateRangeSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        try:
            creds = get_credentials(user)
            calendar_service = build("calendar", "v3", credentials=creds)
            tasks_service = build("tasks", "v1", credentials=creds)

            # Default to the current month if no dates are provided
            if not start_date or not end_date:
                now = datetime.datetime.now()
                start_date = datetime.datetime(now.year, now.month, 1).isoformat() + 'Z'
                end_date = datetime.datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1], 23, 59, 59).isoformat() + 'Z'
            else:
                start_date = start_date.isoformat() + 'Z'
                end_date = end_date.isoformat() + 'Z'

            # Fetch Calendar Events
            events_result = calendar_service.events().list(
                calendarId="primary",
                timeMin=start_date,
                timeMax=end_date,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])
            events_data = [EventSerializer(event).data for event in events]

            # Fetch Tasks
            tasks_result = tasks_service.tasks().list(tasklist='@default').execute()
            tasks = tasks_result.get('items', [])
            tasks_data = [TaskSerializer(task).data for task in tasks]

            return Response({"events": events_data, "tasks": tasks_data}, status=status.HTTP_200_OK)
        except HttpError as error:
            print(f"An error occurred: {error}")
            return Response({"error": "An error occurred while fetching data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
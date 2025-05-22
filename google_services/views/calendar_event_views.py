from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google_services.serializers import EventSerializer
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from google_services.views.calendar_view import get_credentials
import uuid

class UpdateEventView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        event_id = pk
        event_details = request.data
        creds = get_credentials(request.user)
        service = build('calendar', 'v3', credentials=creds)

        try:
            event = service.events().get(calendarId='primary', eventId=event_id).execute()

            event['summary'] = event_details.get('summary', event['summary'])
            event['location'] = event_details.get('location', event.get('location', ''))
            event['description'] = event_details.get('description', event.get('description', ''))
            event['start']['dateTime'] = event_details.get('start_datetime', event['start']['dateTime'])
            event['end']['dateTime'] = event_details.get('end_datetime', event['end']['dateTime'])
            event['attendees'] = event_details.get('attendees', event.get('attendees', []))
            event['reminders']['useDefault'] = event_details.get('use_default_reminders', True)

            if event_details.get('include_google_meet', False):
                event['conferenceData'] = {
                    'createRequest': {
                        'requestId': str(uuid.uuid4()),
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        },
                    }
                }

            updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

            response_data = {
                'event_updated': True,
                'event_link': updated_event.get('htmlLink'),
                'google_meet_link': updated_event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', None)
            }
            return Response(response_data)

        except HttpError as error:
            print(f"An error occurred: {error}")
            return Response({"error": "Failed to update event"}, status=500)

class DeleteEventView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk=None):
        event_id = pk
        creds = get_credentials(request.user)
        service = build('calendar', 'v3', credentials=creds)

        try:
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            return Response({"message": "Event deleted successfully"}, status=204)
        except HttpError as error:
            print(f"An error occurred: {error}")
            return Response({"error": "Failed to delete event"}, status=500)



class CreateEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event_details = serializer.validated_data
            creds = get_credentials(request.user)
            service = build('calendar', 'v3', credentials=creds)

            event = {
                'summary': event_details.get('summary', 'Meeting'),
                'location': event_details.get('location', 'Online'),
                'description': event_details.get('description', 'A virtual meeting.'),
                'start': {
                    'dateTime': event_details.get('start_datetime').isoformat(),
                    'timeZone': event_details.get('time_zone'),
                },
                'end': {
                    'dateTime': event_details.get('end_datetime').isoformat(),
                    'timeZone': event_details.get('time_zone'),
                },
                'attendees': [{'email': email} for email in event_details.get('attendees', [])],
                'reminders': {
                    'useDefault': event_details.get('use_default_reminders', True),
                },
            }

            if event_details.get('include_google_meet', False):
                event['conferenceData'] = {
                    'createRequest': {
                        'requestId': str(uuid.uuid4()),
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        },
                    }
                }

            try:
                calendar_id = 'primary'
                event = service.events().insert(
                    calendarId=calendar_id,
                    body=event,
                    conferenceDataVersion=1 if 'conferenceData' in event else None
                ).execute()

                response_data = {
                    'event_created': True,
                    'event_link': event.get('htmlLink'),
                    'google_meet_link': event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', None)
                }
                return Response(response_data)
            except HttpError as error:
                print(f"An error occurred: {error}")
                return Response({"error": "Failed to create event"}, status=500)
        else:
            return Response(serializer.errors, status=400)


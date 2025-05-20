from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from web.models import Meeting, User
from xmeeting.models import Employee, XMeeting, XMeetingParticipant, Recording, XMeetingTranscript
from datetime import timedelta
import logging
from examples.whisper_diarization_format import whisper_diarization_format

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Sync meeting data into xmeeting models."

    

    def create_new_models_data(self, meeting_id):
        try:
            meeting = get_object_or_404(Meeting, pk=meeting_id)
            user = meeting.created_by

            start_datetime = meeting.created_at - timedelta(seconds=meeting.length)

            # Create Employee
            employee, _ = Employee.objects.get_or_create(
                username=user.username,
                user_id=user.id,
                unit_id=user.unit_id
            )

            # Create XMeeting
            xmeeting = XMeeting.objects.create(
                xmeeting_title=meeting.name,
                user_id=user.id,
                unit_id=meeting.unit.id,
                xmeeting_date=meeting.created_at.date(),
                start_time=start_datetime.time(),
                end_time=meeting.created_at.time(),
                duration_minutes=meeting.length // 60,
                organizer=employee,
            )

            # Add participants
            XMeetingParticipant.objects.create(
                xmeeting=xmeeting,
                employee=employee,
                role=XMeetingParticipant.ROLE_ORGANIZER,
                attendance_status=XMeetingParticipant.ATTENDANCE_ATTENDED,
                user_id=user.id,
                unit_id=meeting.unit.id
            )

            # Add Recording
            Recording.objects.create(
                xmeeting=xmeeting,
                recording_url=meeting.recording_file_url + meeting.filename,
                file_format=Recording.FORMAT_WAV,
                duration_minutes=meeting.length // 60,
                user_id=user.id,
                unit_id=meeting.unit.id,
            )

            # Add Transcripts
            transcription = whisper_diarization_format(meeting.created_by.pk, meeting_id)
            XMeetingTranscript.objects.create(
                xmeeting=xmeeting,
                unit_id=meeting.unit.id,
                user_id=user.id,
                transcript_text=transcription,
            )

            logger.info(f"Successfully synced meeting ID {meeting_id}.")

        except ObjectDoesNotExist as e:
            logger.error(f"Error syncing meeting: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    def handle(self, *args, **options):
        meeting_id = options.get('meeting_id')

        if meeting_id:
            # Process a single meeting
            self.create_new_models_data(meeting_id)
            self.stdout.write(self.style.SUCCESS(f"Successfully synced meeting ID {meeting_id}"))
        else:
            # Process all meetings
            meetings = Meeting.objects.all()
            if not meetings.exists():
                self.stdout.write(self.style.WARNING("No meetings found in the database."))
                return

            for meeting in meetings:
                self.create_new_models_data(meeting.id)
                self.stdout.write(self.style.SUCCESS(f"Successfully synced meeting ID {meeting.id}"))


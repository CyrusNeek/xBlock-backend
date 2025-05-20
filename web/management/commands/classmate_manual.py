from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from web.models import Meeting, User
from xmeeting.models import Employee, XMeeting, XMeetingParticipant, XMeetingTranscript
from datetime import timedelta
import logging
from examples.whisper_diarization_format import whisper_diarization_format
from vtk.models import (
    XClassmate,
    XClassmateQuiz,
    VTKUser,
    Recording,
    Transcription,
    LanguageSupported,
)
from examples.whisper_diarization_format import whisper_vtk_diarization_format

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Sync meeting data into xmeeting models."

    

    def create_new_models_data(self, xclassmate_id):
        try:
            from django.shortcuts import get_object_or_404
            from django.core.exceptions import ObjectDoesNotExist
            from datetime import datetime
            import logging

            logger = logging.getLogger(__name__)

            try:
                # Fetch XClassmate object
                try:
                    xclassmate = get_object_or_404(XClassmate, pk=xclassmate_id)
                    logger.info(f"Fetched XClassmate with ID: {xclassmate_id}")
                except ObjectDoesNotExist as e:
                    logger.error(f"XClassmate with ID {xclassmate_id} does not exist: {e}")
                    raise

                # Fetch User object
                try:
                    user = get_object_or_404(User, pk=xclassmate.created_by.pk)
                    logger.info(f"Fetched User with ID: {xclassmate.created_by.pk}")
                except ObjectDoesNotExist as e:
                    logger.error(f"User with ID {xclassmate.created_by.pk} does not exist: {e}")
                    raise

                # Create or get LanguageSupported
                try:
                    language, _ = LanguageSupported.objects.get_or_create(
                        language_code="en_US", language_name="English (US)", is_supported=True
                    )
                    logger.info("Fetched or created LanguageSupported for English (US)")
                except Exception as e:
                    logger.error(f"Error creating or fetching LanguageSupported: {e}")
                    raise

                # Create or get VTKUser
                try:
                    vtk_user, _ = VTKUser.objects.get_or_create(
                        email=user.email
                    )
                    logger.info(f"Fetched or created VTKUser with email: {user.email}")
                except Exception as e:
                    logger.error(f"Error creating or fetching VTKUser: {e}")
                    raise

                # Create Recording object
                try:
                    recording = Recording.objects.create(
                        user=vtk_user,
                        recording_title=xclassmate.name,
                        recording_date=xclassmate.created_at.date(),
                        recording_time=xclassmate.created_at.time(),
                        duration_seconds=xclassmate.length,
                        audio_file_path=f"{xclassmate.recording_file_url}{xclassmate.filename}",
                        language=language
                    )
                    logger.info(f"Created Recording with ID: {recording.pk}")
                except Exception as e:
                    logger.error(f"Error creating Recording: {e}")
                    raise

                # Generate transcription text
                try:
                    transcription_text = whisper_vtk_diarization_format(user.pk, xclassmate.pk)
                    logger.info("Generated transcription text")
                except Exception as e:
                    logger.error(f"Error generating transcription text: {e}")
                    raise

                # Create Transcription object
                try:
                    Transcription.objects.create(
                        recording=recording,
                        transcription_text=transcription_text,
                        language=language,
                        transcription_service=Transcription.TranscriptionService.WHISPER,
                        transcription_date=xclassmate.created_at.date(),
                    )
                    logger.info("Created Transcription for recording")
                except Exception as e:
                    logger.error(f"Error creating Transcription: {e}")
                    raise

                # Create Spanish Transcription if translated_summary exists
                if xclassmate.translated_summary:
                    try:
                        spanish_language, _ = LanguageSupported.objects.get_or_create(
                            language_code='es',
                            language_name='Spanish',
                            is_supported=True,
                        )
                        logger.info("Fetched or created LanguageSupported for Spanish")

                        Transcription.objects.create(
                            recording=recording,
                            transcription_text=xclassmate.translated_summary,
                            language=spanish_language,
                            transcription_service=Transcription.TranscriptionService.WHISPER,
                            transcription_date=xclassmate.created_at.date(),
                        )
                        logger.info("Created Spanish Transcription")
                    except Exception as e:
                        logger.error(f"Error creating Spanish Transcription: {e}")
                        raise

                logger.info(f"Successfully created AI models data for XClassmate ID: {xclassmate_id}")

            except ObjectDoesNotExist as e:
                logger.error(f"Object does not exist: {e}")

            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")


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
            meetings = XClassmate.objects.all()
            if not meetings.exists():
                self.stdout.write(self.style.WARNING("No meetings found in the database."))
                return

            for meeting in meetings:
                self.create_new_models_data(meeting.id)
                self.stdout.write(self.style.SUCCESS(f"Successfully synced meeting ID {meeting.id}"))


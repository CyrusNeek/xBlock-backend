import logging
from web.services import Whisper
from web.models import Meeting, MeetingParticipant
from celery import shared_task
from web.tasks import (
    task_summarize_meeting,
    task_extract_meeting_tasks,
    task_meeting_diarization,
    task_extract_meeting_quizzes,
    task_extract_meeting_report,
    task_create_new_models_data
)
from web.utils import PushNotification
from report.tasks.periodic.openai_helper import upload_pdf_to_open_ai, update_assistant_files
import json


logger = logging.getLogger(__name__)

@shared_task
def task_update_whisper_diarization():
    """
    Check if diarization finished or not
    """
    meetings = Meeting.objects.filter(diarization_triggered=False, uploaded=True)

    whisper = Whisper()
    for meeting in meetings:
        try:
            response = "document type : Meeting " + meeting.name + " " + str(meeting.created_at) + " " + meeting.purpose + " " +  "participant counts : " + str(meeting.participants_count) + " "
            
            whisper_text = whisper.retrieve_user_voice(
                user_id=meeting.created_by.id,
                meeting_id=meeting.id,
            )
            response += whisper_text["summary"]
            
            whisper_full_text = whisper.get_whisper_full_text(meeting,False)

            participants = MeetingParticipant.objects.filter(meeting=meeting).all()
            participant_list = ', '.join([f'{p.full_name} ({p.email}) and role : ({p.role}) .' for p in participants])

            openai_file_content = f"""this is the metadata for the file 
            name : {meeting.name},
            created at : {meeting.created_at},
            purpose : {meeting.purpose},
            source link : https://app.xblock.ai/meeting-organizer/detail/{meeting.id} ,
            document type : meeting ,
            unit or physical location : {meeting.unit.address},
            meeting online address : {meeting.online_meeting_url},
            meeting online platform : {meeting.online_meeting_platform},
            participants : {participant_list},
            
            
            """
            openai_file_content += whisper_full_text

            pdf = upload_pdf_to_open_ai(openai_file_content)


            if isinstance(whisper_text, str):
                try:
                    whisper_text = json.loads(whisper_text)  
                except json.JSONDecodeError:
                    print(f"Error: Failed to decode whisper_text: {whisper_text}")
                    whisper_text = {} 

            if whisper_text.get("status") == "Done":
                meeting.diarization_triggered = True
                meeting.file_id = pdf.id
                print(pdf)

            response = whisper.retrieve_user_voice(
            user_id=meeting.created_by.id, meeting_id=meeting.id)
        
            if whisper_text.get('status') == "Done":
                
                logger.info(f"Triggering task_summarize_meeting for meeting {meeting.id}")
                task_summarize_meeting.delay(meeting.id)

                logger.info(f"Triggering task_extract_meeting_tasks for meeting {meeting.id}")
                task_extract_meeting_tasks.delay(meeting.id)

                logger.info(
                    f"Triggering task_extract_meeting_quizzes for meeting {meeting.id}"
                )
                task_extract_meeting_quizzes.delay(meeting.id)

                logger.info(f"Triggering task_extract_meeting_report for meeting {meeting.id}")
                task_extract_meeting_report.delay(meeting.id)
                
                meeting.diarization_triggered = True
                meeting.participants_count = int(response.get("speakers_count"))
                meeting.file_id = pdf.id
                meeting.full_content = whisper_full_text
                meeting.save(update_fields=["diarization_triggered", "participants_count", "file_id", "full_content"])

                task_create_new_models_data(meeting.id)
                notif = PushNotification()
                notif.send_notification(user=meeting.created_by, title=f"Meeting {meeting.name}", body="Your meeting diarization has been ended!", data={'meeting_id':meeting.id})

        except Exception as e:
            # Log the error and continue with the next xclassmate
            logger.error(f"Failed to process xclassmate {meeting.id}: {e}")
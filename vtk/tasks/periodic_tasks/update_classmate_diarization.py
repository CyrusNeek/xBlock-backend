import logging
from web.services import Whisper
from vtk.models import XClassmate
from django.db import connection
from celery import shared_task
from vtk.tasks import (
    task_summarize_xclassmate,
    task_extract_xclassmate_tasks,
    task_extract_xclassmate_quizzes,
    task_extract_xclassmate_report,
    task_create_new_models_data
)
from web.utils import PushNotification
from report.tasks.periodic.openai_helper import upload_pdf_to_open_ai
logger = logging.getLogger(__name__)
import json


@shared_task
def task_update_whisper_classmate_diarization():
    """
    Check if diarization finished or not
    """
    xclassmates = XClassmate.objects.filter(diarization_triggered=False, uploaded=True)
    whisper = Whisper()
    for xclassmate in xclassmates:
        try:
            # Attempt to process the xclassmate
            response = xclassmate.name + " " + str(xclassmate.created_at) + " " + xclassmate.purpose + " "+ "participant counts : " + str(xclassmate.participants_count) + " "
            
            whisper_text = whisper.retrieve_user_voice(
                user_id=xclassmate.created_by.id,
                meeting_id=xclassmate.id,
                is_xclassmate=True,
            )

            
            response += whisper_text["summary"]
            whisper_full_text = whisper.get_whisper_full_text(xclassmate,True)

            openai_file_content = f'''this is the metadata for the file
            name : {xclassmate.name},
            created at : {xclassmate.created_at},
            purpose : {xclassmate.purpose},
            source link : https://app.xblock.ai/speech-knowledges/detail/{xclassmate.id} ,
            document type : xclassmate or speech to knowledge,


            '''
            openai_file_content += whisper_full_text

            pdf = upload_pdf_to_open_ai(openai_file_content)

            if isinstance(whisper_text, str):
                try:
                    whisper_text = json.loads(whisper_text)  
                except json.JSONDecodeError:
                    print(f"Error: Failed to decode whisper_text: {whisper_text}")
                    whisper_text = {} 

            if whisper_text.get("status") == "Done":
                xclassmate.diarization_triggered = True
                xclassmate.file_id = pdf.id
                print(pdf)
                
                xclassmate.participants_count = int(whisper_text.get("speakers_count", 0))
                xclassmate.full_content = whisper_full_text
                xclassmate.save(
                    update_fields=["diarization_triggered", "participants_count","file_id", "full_content"]
                )

                logger.info(
                    f"Triggering task_summarize_xclassmate for xclassmate {xclassmate.id}"
                )
                task_summarize_xclassmate.delay(xclassmate.id)

                logger.info(
                    f"Triggering task_extract_xclassmate_tasks for xclassmate {xclassmate.id}"
                )
                task_extract_xclassmate_tasks.delay(xclassmate.id)

                logger.info(
                    f"Triggering task_extract_xclassmate_quizzes for xclassmate {xclassmate.id}"
                )
                task_extract_xclassmate_quizzes.delay(xclassmate.id)

                logger.info(
                    f"Triggering task_extract_xclassmate_report for xclassmate {xclassmate.id}"
                )
                task_extract_xclassmate_report.delay(xclassmate.id)

                logger.info(
                    f"Triggering task_create_new_models_data for xclassmate {xclassmate.id}"
                )
                task_create_new_models_data(xclassmate.id)

                notif = PushNotification()
                notif.send_notification(
                    user=xclassmate.created_by,
                    title=f"voice to knowledge: {xclassmate.name}",
                    body="Your voice to knowledge diarization has been ended!",
                    data={"xclassmate_id": xclassmate.id},
                )
                logger.info(f"Successfully processed xclassmate {xclassmate.id}")

        except Exception as e:
            # Log the error and continue with the next xclassmate
            logger.error(f"Failed to process xclassmate {xclassmate.id}: {e}")


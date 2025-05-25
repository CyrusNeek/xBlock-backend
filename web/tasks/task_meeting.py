from django.utils import timezone
from celery import shared_task
from web.models.assistant import Assistant
from web.services.storage_service import StorageService
from web.verba_assistant import VerbaAssistant
from examples.whisper_diarization_format import whisper_diarization_format, whisper_vtk_diarization_format

from ..models import Meeting, Task, MeetingQuiz
from openai import OpenAI
import logging
import json
from django.conf import settings
from report.tasks.periodic.openai_helper import (
    write_chunk,
    create_or_retrieve_vector_store,
)
from web.models import OpenAIFile
from web.services import Whisper

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def translate_meeting_data(data):
    try:
        prompt = 'Translate the following data (text, JSON, list, or any other format) into Spanish without adding any extra information or modifying numbers, names, or special terms. The final result should always be plain text'
    
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": f"Summarize the meeting: {data}",
                },
            ],
            temperature=0,
        )
        return str(response.choices[0].message.content)
    
    except:
        logger.info("translate has an error")
        


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_summarize_meeting(self, meeting_id):
    logger.info("Executing task_summarize_meeting")

    try:
        meeting = Meeting.objects.get(id=meeting_id)
        
        content = whisper_diarization_format(meeting_id=meeting.id, user_id=meeting.created_by.pk)
        
        prompt =  '''You are provided with a JSON file containing the transcription of a meeting. The JSON structure includes metadata (such as file name, user ID, and meeting ID) and a series of dialogues. Each dialogue entry contains timestamps, text, and speaker information.

                Your task is to generate a concise and well-organized summary of the meeting based on the provided content. The summary should be clear, to the point, and include all valuable information without omitting critical details.

                Input Structure:

                A JSON file containing dialogues, each with text, start and end times, and speaker details.
                Output Structure:

                A brief and well-constructed summary in plain text format.
                Instructions:

                Review the entire meeting content.
                Identify and summarize the main topics discussed.
                Highlight key points, decisions, action items, and any relevant outcomes.
                Ensure the summary is clear, concise, and covers the most important aspects of the meeting without unnecessary detail.
                Example Output:

                "The meeting began with [Speaker's Name] outlining [Main Topic]. Key discussions included [Brief Summary of Discussion Points]. The team decided on [Decisions/Actions]. [Speaker's Name] highlighted [Important Note or Takeaway]. The meeting concluded with [Summary of Conclusion/Next Steps].

                Overall, the focus was on [Overall Purpose/Outcome], with special attention given to [Specific Detail]."

                Generate a summary that effectively captures the essence of the meeting, suitable for quick reading and reference in business settings.
            '''

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": f"Summarize the meeting: {content}",
                },
            ],
            temperature=0,
        )

        # Log the full response to inspect it
        logger.info(f"Full OpenAI response: {response}")

        summary_text = str(response.choices[0].message.content)

        meeting.summary = [summary_text]
        meeting.translated_summary = translate_meeting_data(summary_text)
        meeting.save(update_fields=["summary", "translated_summary"])
        logger.info(f"Meeting summary saved: {meeting.summary}")

    except Exception as e:
        logger.error(f"Error in task_summarize_meeting: {e}")

@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_extract_meeting_tasks(self, meeting_id):
    logger.info("Executing task_extract_meeting_tasks")

    try:
        meeting = Meeting.objects.get(id=meeting_id)
        
        content = whisper_diarization_format(meeting_id=meeting.id, user_id=meeting.created_by.pk)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Extracting tasks only based on meeting notes content and presenting them in a structured JSON format. Please ensure that the extracted tasks are listed under a 'tasks' key, and each task is formatted as a string within an array",
                },
                {
                    "role": "user",
                    "content": f"Extract core tasks from the following meeting notes: {content}",
                },
            ],
            temperature=0,
        )
        # Parse the response
        tasks_json = json.loads(response.choices[0].message.content)

        # Iterate over the tasks and create Task instances
        for task_desc in tasks_json["tasks"]:
            Task.objects.create(
                created_by=meeting.created_by,
                assignee=None,
                description=task_desc,
                meeting=meeting,
            )

        vector_store_id = create_or_retrieve_vector_store(meeting.unit, "global").id

        upload_tasks_to_openai(
            tasks_json["tasks"],
            meeting.id,
            meeting.name,
            vector_store_id,
        )

    except Exception as e:
        logger.error(f"Error in task_summarize_meeting: {e}")


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_extract_meeting_quizzes(self, meeting_id):
    logger.info("Executing task_extract_meeting_quizzes")

    try:
        meeting = Meeting.objects.get(id=meeting_id)
        
        content = whisper_diarization_format(meeting_id=meeting.id, user_id=meeting.created_by.pk)

        prompt = """
        You are given a JSON file containing the transcription of a meeting. The JSON structure includes metadata (like file name, user ID, and meeting ID) and a series of dialogues. Each dialogue contains timestamps, text, and speaker information.
Your task is to generate questions based on the content of the meeting. Each question should have multiple answer options, with one or more options marked as correct or incorrect.
Input Structure:
A JSON file containing dialogues, each with text, start and end times, and speaker details.

Output Structure:

- A list of questions in JSON format, each with:
    - text: The question text.
    - answers: A list of possible answers, each with:
            -text: The answer option.
            -is_correct: A boolean indicating if the option is correct.

Instructions:

    Analyze the meeting content.
    Extract key points to formulate questions.
    Provide relevant answer options, marking them as correct or incorrect.

Example Output:
[
    {
        "text": "text of the generated question",
        "answers": [
            {"text": "correct answer option", "is_correct": True/False},
            {"text": "incorrect answer option", "is_correct": True/False}
        ]
    },
    {
        "text": "text of another generated question",
        "answers": [
            {"text": "correct answer option", "is_correct": True/False},
            {"text": "another incorrect answer option", "is_correct": True/False}
        ]
    }
]

Generate questions that reflect the main ideas and details discussed in the meeting.
Only respond with a minified JSON. No further explanation or additional content is needed.
        """

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{prompt}"},
                {"role": "user", "content": f"{content}"},
            ],
            temperature=0,
        )
        completion.choices[0].message.content.replace("```json", "").replace("```", "")
        quizzes_json = json.loads(completion.choices[0].message.content)

        # Iterate over the quizzes and create Quiz instances
        for quiz in quizzes_json:
            MeetingQuiz.objects.create(
                user=meeting.created_by,
                text=quiz["text"],
                choices=quiz["answers"],
                meeting=meeting,
            )

    except Exception as e:
        logger.error(f"Error in generation of quizzes: {e}")


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_extract_meeting_report(self, meeting_id):
    logger.info("Executing task_extract_meeting_report")

    try:
        meeting = Meeting.objects.get(id=meeting_id)
        
        content = whisper_diarization_format(meeting_id=meeting.id, user_id=meeting.created_by.pk)

        prompt = """
        You are provided with a JSON file containing the transcription of a meeting. The JSON structure includes metadata (such as file name, user ID, and meeting ID) and a series of dialogues. Each dialogue entry contains timestamps, text, and speaker information.
        Your task is to generate a comprehensive report of the meeting based on the content provided. The report should summarize the key points, discussions, decisions, and any other relevant details that occurred during the meeting. The output should be a well-structured and detailed string of text.
        Input Structure:
        A JSON file containing dialogues, each with text, start and end times, and speaker details.

        Output Structure:
        A detailed report in plain text format.

        Instructions:
        1. Review the entire content of the meeting.
        2. Identify and summarize the main topics discussed.
        3. Highlight important decisions, action items, or conclusions reached during the meeting.
        4. Ensure the report is clear, comprehensive, and well-organized, covering all critical aspects of the meeting.

        Example Output:
        "The meeting commenced with an introduction by [Speaker's Name], who welcomed [Participant's Name] to discuss [Meeting Topic]. Key points discussed include [Summary of Discussion]. The team agreed on [Decisions/Actions], and [Speaker's Name] emphasized the importance of [Key Takeaway]. The meeting concluded with [Conclusion/Next Steps].
        Overall, the meeting focused on [Overall Purpose/Outcome], with a particular emphasis on [Specific Details]."
        ##Generate a report that provides a thorough and clear summary of the meeting, suitable for professional, academic, or business settings.
        Only respond with just the text of the report. No further explanation or additional content is needed.
        """

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{prompt}"},
                {"role": "user", "content": f"{content}"},
            ],
            temperature=0,
        )
        res = str(completion.choices[0].message.content)
        meeting.report = res
        meeting.translated_report = translate_meeting_data(res)
        meeting.save(update_fields=["report", "translated_report"])

    except Exception as e:
        logger.error(f"Error in generation of report: {e}")


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_meeting_diarization(self, meeting_id):
    logger.info(f"Executing diarization task meeting_id: {meeting_id}")
    meeting = Meeting.objects.get(id=meeting_id)
    if not meeting.recording_file_url:
        raise Exception("No recording URL found for the meeting.")
    if meeting.diarization_signal_triggered:
        raise Exception(f"Diarization already done for id {meeting.id}")

    logger.info(f"Mark {meeting_id} diarization_triggered to True")
    meeting.diarization_signal_triggered = True
    # meeting.save()

    # file_name = meeting.recording_file_url.split("/")[-1]
    # presigned_url = StorageService().generate_presigned_download_url(
    #     settings.BUCKET_MEETING_FOLDER + "/" + file_name
    # )

    # meeting_filename = meeting.filename.split("/")[-1]
    # StorageService().download_file(meeting.filename, meeting_filename)

    file_url = f"{meeting.recording_file_url}{meeting.filename}"
    # instance = Whisper().diarization(file_url, meeting.name, meeting.created_by.id, meeting_id)
    instance = Whisper().diarization(file_url, meeting_id)

    # print(diarization)
    # if diarization:
    #     logger.info(f"Saving Diarization result: {diarization}")
    #     meeting.diarization = diarization
    #     meeting.diarization_triggered = True
    #     upload_meeting_to_openai(
    #         diarization,
    #         meeting_id,
    #         meeting.name,
    #     )

    #     meeting.save()
    logger.info("Diarization Results: ")
    logger.info(instance)
    meeting.diarization_id = instance.get("id")
    meeting.save(update_fields=["diarization_id", "diarization_signal_triggered"])
    return f"Diarization started {meeting.name}"


def upload_meeting_to_openai(diarization, meeting_id, meeting_name):
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    filename = write_chunk(
        diarization, f"meeting_{meeting_name}_{meeting_id}_{timestamp}"
    )

    file = OpenAIFile.objects.create(
        file_id="-1",
        file_name=filename,
        unit=Meeting.objects.get(pk=meeting_id).unit,
        model_name="meeting",
    )

    verba = VerbaAssistant()

    verba.upload_document([file])

    return file

    # for assistant in assistants:
    #     client.beta.vector_stores.files.create(
    #         vector_store_id=assistant.vector_store_id, file_id=file_id
    #     )
    #     assistant.files.add(file)
    #     assistant.save()

    # update_assistant_vectors(assistant)
    # client.beta.assistants.update(
    #     assistant_id=assistant.assistant_id,
    #     tool_resources={"file_search": {"vector_store_ids": [vector_id]}},
    # )


def upload_tasks_to_openai(tasks, meeting_id, meeting_name):
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")

    filename = write_chunk(
        tasks, f"tasks_for_meeting_{meeting_name}_{meeting_id}_{timestamp}"
    )

    verba = VerbaAssistant()

    # file_id = client.files.create(
    #     purpose="assistants",
    #     file=open(filename, "rb"),
    # ).id

    file = OpenAIFile.objects.create(
        file_id="-2",
        file_name=filename,
        unit=Meeting.objects.get(pk=meeting_id).unit,
        model_name="task",
    )

    verba.upload_document([file])

    # vector_store_file = client.beta.vector_stores.files.create(
    #     vector_store_id=vector_id, file_id=file_id
    # )

    # assistants = Assistant.objects.filter(
    #     user__in=Meeting.objects.get(pk=meeting_id).unit.users.all(),
    #     purpose=Assistant.PURPOSE_DEFAULT,
    # )

    # for assistant in assistants:
    #     client.beta.vector_stores.files.create(
    #         vector_store_id=assistant.vector_store_id, file_id=file_id
    #     )

    #     assistant.files.add(file)
    #     assistant.save()

    #     # client.beta.assistants.update(
    #     #     assistant_id=assistant.assistant_id,
    #     #     tool_resources={"file_search": {"vector_store_ids": [vector_id]}},
    #     # )
    #     # update_assistant_vectors(assistant)



@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_create_new_models_data(self, meeting_id):
    from django.shortcuts import get_object_or_404
    from django.core.exceptions import ObjectDoesNotExist
    from web.models import User
    from datetime import datetime, timedelta
    from web.constants import WhisperLanguages
    from xmeeting.models import (
        XMeeting,
        Employee,
        Recording,
        XMeetingTranscript,
        XMeetingParticipant,
    )

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

    # try:
    #     meeting = get_object_or_404(Meeting, pk=meeting_id) 
    #     user = get_object_or_404(User, pk=meeting.created_by.pk)

    #     created_at_time = meeting.created_at
    #     start_datetime = created_at_time - timedelta(seconds=meeting.length)

    #     employee, _ = Employee.objects.get_or_create(
    #         username=user.username,
    #         user_id=user.id
    #     )

    #     xmeeting = XMeeting.objects.create(
    #         xmeeting_title=meeting.name,
    #         user_id=meeting.created_by.id ,
    #         unit_id=meeting.unit.id,
    #         xmeeting_date=meeting.created_at.date(),
    #         start_time=start_datetime.time(),
    #         end_time=meeting.created_at.time(),
    #         duration_minutes=meeting.length // 60,
    #         organizer=employee,
    #         xmeeting_type=XMeeting.TEAM_MEETING,
    #         platform=XMeeting.PLATFORM_XBLOCK,
    #         location=f"{meeting.recording_file_url}{meeting.filename}",
    #     )
        
    #     XMeetingParticipant.objects.create(
    #         xmeeting=xmeeting,
    #         employee=employee,
    #         role=XMeetingParticipant.ROLE_ORGANIZER,
    #         attendance_status=XMeetingParticipant.ATTENDANCE_ATTENDED,
    #     )

    #     recording = Recording.objects.create(
    #         xmeeting=xmeeting,
    #         recording_url=meeting.recording_file_url + meeting.filename,
    #         file_format=Recording.FORMAT_WAV,
    #         file_size_mb=0,
    #         duration_minutes=meeting.length // 60,
    #         storage_location=Recording.STORAGE_GOOGLE_BUCKET,
    #         access_level=Recording.ACCESS_INTERNAL,
    #         user_id=user.id,
    #         unit_id=meeting.uint.id
    #     )


    #     transcription = whisper_diarization_format(meeting.created_by.pk, meeting_id)

    #     XMeetingTranscript.objects.create(
    #         xmeeting=xmeeting,
    #         unit_id=meeting.unit.id,
    #         user_id=user.id,
    #         transcript_text=transcription,
    #         language=WhisperLanguages.ENGLISH.value,
    #     )

    #     if meeting.translated_summary:
    #         XMeetingTranscript.objects.create(
    #             xmeeting=xmeeting,
    #             unit_id=meeting.unit.id,
    #             user_id=user.id,
    #             transcript_text=meeting.translated_summary,
    #             language=WhisperLanguages.SPANISH.value,
    #         )

    #     logger.info(f"Successfully created AI models data for meeting ID: {meeting_id}")

    # except ObjectDoesNotExist as e:
    #     logger.error(f"Object does not exist: {e}")
    #     self.retry(countdown=self.default_retry_delay)
    # except Exception as e:
    #     logger.error(f"An error occurred: {e}")
    #     self.retry(countdown=self.default_retry_delay)


def create_meeting_participants(user_id, meeting_id):
    from django.shortcuts import get_object_or_404
    from datetime import timedelta
    from web.models import User
    from xmeeting.models import Employee, XMeetingParticipant, XMeeting
    from django.core.exceptions import ObjectDoesNotExist

    
    try:
        meeting = Meeting.objects.get(pk=meeting_id)
        user = User.objects.get(pk=user_id)

        employee, _ = Employee.objects.get_or_create(
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            email=user.email,
        )

        xmeeting = XMeeting.objects.get(
            xmeeting_title=meeting.name,
            xmeeting_date=meeting.created_at.date(),
            duration_minutes=meeting.length // 60
        )

        XMeetingParticipant.objects.create(
            xmeeting=xmeeting,
            employee=employee,
            role=XMeetingParticipant.ROLE_PARTICIPANT,
            attendance_status=XMeetingParticipant.ATTENDANCE_ATTENDED,
        )

    except Meeting.DoesNotExist:
        logger.error(f"Meeting with ID {meeting_id} does not exist.")
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist.")
    except ObjectDoesNotExist as e:
        logger.error(f"Participants Object does not exist: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

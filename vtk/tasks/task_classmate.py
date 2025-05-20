from django.utils import timezone
from celery import shared_task
from vtk.models.content_type import ContentType
from vtk.models.generated_content import GeneratedContent
from web.models.user import User
from web.verba_assistant import VerbaAssistant
from examples.whisper_diarization_format import whisper_vtk_diarization_format
from vtk.models import (
    XClassmate,
    XClassmateQuiz,
    VTKUser,
    Recording,
    Transcription,
    LanguageSupported,
)
from web.models import Task
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


def translate_xclassmate_data(data):
    try:
        prompt = "Translate the following data (text, JSON, list, or any other format) into Spanish without adding any extra information or modifying numbers, names, or special terms. The final result should always be plain text"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": f"Summarize the xclassmate: {data}",
                },
            ],
            temperature=0,
        )
        return str(response.choices[0].message.content)

    except:
        logger.info("translate has an error")


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_summarize_xclassmate(self, xclassmate_id):
    logger.info("Executing task_summarize_xclassmate")

    try:
        xclassmate = XClassmate.objects.get(id=xclassmate_id)

        content = whisper_vtk_diarization_format(
            xclassmate_id=xclassmate.id, user_id=xclassmate.created_by.pk
        )

        prompt = """You are provided with a JSON file containing the transcription of a xclassmate. The JSON structure includes metadata (such as file name, user ID, and xclassmate ID) and a series of dialogues. Each dialogue entry contains timestamps, text, and speaker information.

                Your task is to generate a concise and well-organized summary of the xclassmate based on the provided content. The summary should be clear, to the point, and include all valuable information without omitting critical details.

                Input Structure:

                A JSON file containing dialogues, each with text, start and end times, and speaker details.
                Output Structure:

                A brief and well-constructed summary in plain text format.
                Instructions:

                Review the entire xclassmate content.
                Identify and summarize the main topics discussed.
                Highlight key points, decisions, action items, and any relevant outcomes.
                Ensure the summary is clear, concise, and covers the most important aspects of the xclassmate without unnecessary detail.
                Example Output:

                "The xclassmate began with [Speaker's Name] outlining [Main Topic]. Key discussions included [Brief Summary of Discussion Points]. The team decided on [Decisions/Actions]. [Speaker's Name] highlighted [Important Note or Takeaway]. The xclassmate concluded with [Summary of Conclusion/Next Steps].

                Overall, the focus was on [Overall Purpose/Outcome], with special attention given to [Specific Detail]."

                Generate a summary that effectively captures the essence of the xclassmate, suitable for quick reading and reference in business settings.
            """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": f"Summarize the xclassmate: {content}",
                },
            ],
            temperature=0,
        )

        # Log the full response to inspect it
        logger.info(f"Full OpenAI response: {response}")

        summary_text = str(response.choices[0].message.content)

        xclassmate.summary = [summary_text]
        xclassmate.translated_summary = translate_xclassmate_data(summary_text)
        xclassmate.save(update_fields=["summary", "translated_summary"])
        logger.info(f"xclassmate summary saved: {xclassmate.summary}")

    except Exception as e:
        logger.error(f"Error in task_summarize_xclassmate: {e}")


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_extract_xclassmate_tasks(self, xclassmate_id):
    logger.info("Executing task_extract_xclassmate_tasks")

    try:
        xclassmate = XClassmate.objects.get(id=xclassmate_id)

        content = whisper_vtk_diarization_format(
            xclassmate_id=xclassmate.id, user_id=xclassmate.created_by.pk
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Extracting tasks only based on xclassmate notes content and presenting them in a structured JSON format. Please ensure that the extracted tasks are listed under a 'tasks' key, and each task is formatted as a string within an array",
                },
                {
                    "role": "user",
                    "content": f"Extract core tasks from the following xclassmate notes: {content}",
                },
            ],
            temperature=0,
        )
        # Parse the response
        tasks_json = json.loads(response.choices[0].message.content)

        # Iterate over the tasks and create Task instances
        for task_desc in tasks_json["tasks"]:
            Task.objects.create(
                created_by=xclassmate.created_by,
                assignee=None,
                description=task_desc,
                xclassmate=xclassmate,
            )

        vector_store_id = create_or_retrieve_vector_store(xclassmate.unit, "global").id

        upload_tasks_to_openai(
            tasks_json["tasks"],
            xclassmate.id,
            xclassmate.name,
            vector_store_id,
        )

    except Exception as e:
        logger.error(f"Error in task_summarize_xclassmate: {e}")


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_extract_xclassmate_quizzes(self, xclassmate_id):
    logger.info("Executing task_extract_xclassmate_quizzes")

    try:
        xclassmate = XClassmate.objects.get(id=xclassmate_id)

        content = whisper_vtk_diarization_format(
            xclassmate_id=xclassmate.id, user_id=xclassmate.created_by.pk
        )

        prompt = """
        You are given a JSON file containing the transcription of a xclassmate. The JSON structure includes metadata (like file name, user ID, and xclassmate ID) and a series of dialogues. Each dialogue contains timestamps, text, and speaker information.
Your task is to generate questions based on the content of the xclassmate. Each question should have multiple answer options, with one or more options marked as correct or incorrect.
Input Structure:
A JSON file containing dialogues, each with text, start and end times, and speaker details.

Output Structure:

- A list of questions in JSON format, each with:
    - text: The question text.
    - answers: A list of possible answers, each with:
            -text: The answer option.
            -is_correct: A boolean indicating if the option is correct.

Instructions:

    Analyze the xclassmate content.
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

Generate questions that reflect the main ideas and details discussed in the xclassmate.
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
            XClassmateQuiz.objects.create(
                user=xclassmate.created_by,
                text=quiz["text"],
                choices=quiz["answers"],
                xclassmate=xclassmate,
            )

    except Exception as e:
        logger.error(f"Error in generation of quizzes: {e}")


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_extract_xclassmate_report(self, xclassmate_id):
    logger.info("Executing task_extract_xclassmate_report")

    try:
        xclassmate = XClassmate.objects.get(id=xclassmate_id)

        content = whisper_vtk_diarization_format(
            xclassmate_id=xclassmate.id, user_id=xclassmate.created_by.pk
        )

        prompt = """
        You are provided with a JSON file containing the transcription of a xclassmate. The JSON structure includes metadata (such as file name, user ID, and xclassmate ID) and a series of dialogues. Each dialogue entry contains timestamps, text, and speaker information.
        Your task is to generate a comprehensive report of the xclassmate based on the content provided. The report should summarize the key points, discussions, decisions, and any other relevant details that occurred during the xclassmate. The output should be a well-structured and detailed string of text.
        Input Structure:
        A JSON file containing dialogues, each with text, start and end times, and speaker details.

        Output Structure:
        A detailed report in plain text format.

        Instructions:
        1. Review the entire content of the xclassmate.
        2. Identify and summarize the main topics discussed.
        3. Highlight important decisions, action items, or conclusions reached during the xclassmate.
        4. Ensure the report is clear, comprehensive, and well-organized, covering all critical aspects of the xclassmate.

        Example Output:
        "The xclassmate commenced with an introduction by [Speaker's Name], who welcomed [Participant's Name] to discuss [Xclassmate Topic]. Key points discussed include [Summary of Discussion]. The team agreed on [Decisions/Actions], and [Speaker's Name] emphasized the importance of [Key Takeaway]. The xclassmate concluded with [Conclusion/Next Steps].
        Overall, the xclassmate focused on [Overall Purpose/Outcome], with a particular emphasis on [Specific Details]."
        ##Generate a report that provides a thorough and clear summary of the xclassmate, suitable for professional, academic, or business settings.
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
        xclassmate.report = res
        xclassmate.translated_report = translate_xclassmate_data(res)
        xclassmate.save(update_fields=["report", "translated_report"])

    except Exception as e:
        logger.error(f"Error in generation of report: {e}")


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_xclassmate_diarization(self, xclassmate_id):
    logger.info(f"Executing diarization task xclassmate_id: {xclassmate_id}")
    xclassmate = XClassmate.objects.get(id=xclassmate_id)
    if not xclassmate.recording_file_url:
        raise Exception("No recording URL found for the xclassmate.")
    if xclassmate.diarization_signal_triggered:
        raise Exception(f"Diarization already done for id {xclassmate.id}")

    logger.info(f"Mark {xclassmate_id} diarization_triggered to True")
    xclassmate.diarization_signal_triggered = True
    file_url = f"{xclassmate.recording_file_url}{xclassmate.filename}"
    instance = Whisper().diarization(
        file_url, meeting_id=xclassmate_id, is_xclassmate=True
    )

    logger.info("Diarization Results: ")
    logger.info(instance)
    xclassmate.diarization_id = instance.get("id")
    xclassmate.save(update_fields=["diarization_id", "diarization_signal_triggered"])
    return f"Diarization started {xclassmate.name}"


def upload_xclassmate_to_openai(diarization, xclassmate_id, xclassmate_name):
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    filename = write_chunk(
        diarization, f"xclassmate_{xclassmate_name}_{xclassmate_id}_{timestamp}"
    )

    file = OpenAIFile.objects.create(
        file_id="-1",
        file_name=filename,
        unit=XClassmate.objects.get(pk=xclassmate_id).unit,
        model_name="xclassmate",
    )

    verba = VerbaAssistant()

    verba.upload_document([file])

    return file


def upload_tasks_to_openai(tasks, xclassmate_id, xclassmate_name):
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")

    filename = write_chunk(
        tasks, f"tasks_for_xclassmate_{xclassmate_name}_{xclassmate_id}_{timestamp}"
    )

    verba = VerbaAssistant()

    file = OpenAIFile.objects.create(
        file_id="-2",
        file_name=filename,
        unit=XClassmate.objects.get(pk=xclassmate_id).unit,
        model_name="task",
    )

    verba.upload_document([file])


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def task_create_new_models_data(self, xclassmate_id):
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
            vtk_user, vtk_user_created = VTKUser.objects.get_or_create(
                email=user.email
            )
            if vtk_user_created:
                vtk_user.user_id=xclassmate.created_by.id
                vtk_user.unit_id=xclassmate.unit.id
                vtk_user.save()

            logger.info(f"Fetched or created VTKUser with email: {user.email}")
        except Exception as e:
            logger.error(f"Error creating or fetching VTKUser: {e}")
            raise

        # Create Recording object
        try:
            recording = Recording.objects.create(
                stk_user=vtk_user,
                recording_title=xclassmate.name,
                recording_date=xclassmate.created_at.date(),
                recording_time=xclassmate.created_at.time(),
                duration_seconds=xclassmate.length,
                audio_file_path=f"{xclassmate.recording_file_url}{xclassmate.filename}",
                language=language,
                user_id=xclassmate.created_by.id,
                unit_id=xclassmate.unit.id

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
                user_id=xclassmate.created_by.id,
                unit_id=xclassmate.unit.id
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
                    user_id=xclassmate.created_by.id,
                    unit_id=xclassmate.unit.id
                )
                logger.info("Created Spanish Transcription")
            except Exception as e:
                logger.error(f"Error creating Spanish Transcription: {e}")
                raise

        logger.info(f"Successfully created AI models data for XClassmate ID: {xclassmate_id}")

    except ObjectDoesNotExist as e:
        logger.error(f"Object does not exist: {e}")
        self.retry(countdown=self.default_retry_delay)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        self.retry(countdown=self.default_retry_delay)


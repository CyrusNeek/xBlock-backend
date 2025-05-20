import os
import requests
import logging
import json
from requests.exceptions import HTTPError, RequestException
from django.apps import apps
from web.models.meeting import Meeting


class Whisper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_headers(self):
        return {
            "content-type": "application/json",
            "Authorization": f"Basic {os.getenv('WHISPER_API_KEY')}",
        }

    def _handle_request(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            self.logger.info(f"Request successful: {response.status_code} - {url}")
            return response.json()
        except HTTPError as http_err:
            self.logger.error(f"HTTP error occurred: {http_err} - URL: {url}")
            raise
        except RequestException as req_err:
            self.logger.error(f"Request error occurred: {req_err} - URL: {url}")
            raise
        except Exception as err:
            self.logger.error(f"An unexpected error occurred: {err}")
            raise

    def diarization(self, file_url: str, meeting_id: int, is_xclassmate=False) -> dict:
        if is_xclassmate == False:
            meeting = Meeting.objects.get(pk=meeting_id)
        else:
            XClassmate = apps.get_model("vtk", "XClassmate")
            meeting = XClassmate.objects.get(pk=meeting_id)
        url = f'{os.getenv("WHISPER_BASE_URL")}/api/transcribe/{meeting.created_by.id}/'
        payload = json.dumps(
            {
                "audio_file": file_url,
                "file_name": meeting.name,
                "meeting_id": meeting.id,
                "is_xclassmate": is_xclassmate,
            }
        )
        params = {
            "lang": meeting.source_language,
            "target_lang": meeting.target_language,
        }

        return self._handle_request(
            "POST", url, headers=self.get_headers(), data=payload, params=params
        )

    def get_user_voices(self, user_id: int) -> dict:
        url = f'{os.getenv("WHISPER_BASE_URL")}/api/transcribe/{user_id}/'
        return self._handle_request("GET", url, headers=self.get_headers())

    def retrieve_user_voice(
        self,
        user_id: int,
        meeting_id: int,
        page_size: int = 10,
        page_number: int = 1,
        is_xclassmate=False,
    ) -> dict:
        url = f'{os.getenv("WHISPER_BASE_URL")}/api/transcribe/{user_id}/{meeting_id}/'
        params = {
            "page_size": page_size,
            "page": page_number,
            "is_xclassmate": is_xclassmate,
        }
        return self._handle_request(
            "GET", url, headers=self.get_headers(), params=params
        )

    def update_speaker_name(
        self, user_id: int, meeting_id: int, payload: dict, is_xclassmate=False
    ) -> dict:
        url = f'{os.getenv("WHISPER_BASE_URL")}/api/transcribe/{user_id}/{meeting_id}/'
        params = {"is_xclassmate": is_xclassmate}
        return self._handle_request(
            "PUT", url, headers=self.get_headers(), json=payload, params=params
        )

    def retrieve_user_voice_text(
        self, user_id: int, meeting_id: int, is_xclassmate=False
    ) -> dict:
        url = f'{os.getenv("WHISPER_BASE_URL")}/api/transcribe/{user_id}/{meeting_id}/text/'
        params = {"is_xclassmate": is_xclassmate}
        return self._handle_request(
            "GET", url, headers=self.get_headers(), params=params
        )
    
    def get_whisper_full_text(self, meeting, is_classmate : bool):
        page = 1
        output_text = ""

        while True:
            data = self.get_whisper_text(meeting, page, is_classmate)

            if not data or "dialogues" not in data:  
                break

            dialogues = data["dialogues"]
            for dialogue in dialogues.get("results", []):
                speaker = dialogue.get("speaker", "Unknown Speaker")
                text = dialogue.get("text", "").strip()
                output_text += f"{speaker}: {text}\n"

            if dialogues.get("next"):  
                page += 1
            else:
                break  

        return output_text


    def get_whisper_text(self, meeting, page: int, is_calssmate : bool ):
        return self.retrieve_user_voice(
            user_id=meeting.created_by.id,
            meeting_id=meeting.id,
            page_size=100,
            page_number=page,
            is_xclassmate=is_calssmate,
        )

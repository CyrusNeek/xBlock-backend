from web.services.whisper import Whisper
import logging
import json



logger = logging.getLogger(__name__)


def whisper_diarization_format(user_id, meeting_id):
    try:
        whisper = Whisper()
        response = whisper.retrieve_user_voice_text(
                    user_id=user_id,
                    meeting_id=meeting_id,
                )
        return response["text"]
    except Exception as e:
        logger.info(f"whisper_diarization_format has an error: {e}")
        return None


def whisper_vtk_diarization_format(user_id, xclassmate_id):
    try:
        whisper = Whisper()
        response = whisper.retrieve_user_voice_text(
                    user_id=user_id,
                    meeting_id=xclassmate_id,
                    is_xclassmate=True
                )
        return response["text"]
    except Exception as e:
        logger.info(f"whisper_diarization_format has an error: {e}")
        return None
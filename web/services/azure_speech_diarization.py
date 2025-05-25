import time
# Azure diarization deprecated and removed
from pydub import AudioSegment
import requests
from django.conf import settings
import uuid
import logging
import os

logger = logging.getLogger(__name__)

class AzureDiarization:
    def __init__(self, audio_url: str, language="en-US", filename=None):
        self.transcribing_stop = False
        self.filename = filename
        self.filename = self.download_convert_file(audio_url)
        self.result = []
        
        # init azure speech client
        self.speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SUBSCRIPTION_KEY, 
            region=settings.AZURE_SERVICE_REGION,
        )
        self.speech_config.speech_recognition_language = language
        self.audio_config = speechsdk.audio.AudioConfig(filename=self.filename)
        self.conversation_transcriber = speechsdk.transcription.ConversationTranscriber(
            speech_config=self.speech_config, 
            audio_config=self.audio_config
        )
        
        # Connect callbacks to the events fired by the conversation transcriber
        self.conversation_transcriber.transcribed.connect(self.conversation_transcriber_transcribed_cb)
        self.conversation_transcriber.session_started.connect(self.conversation_transcriber_session_started_cb)
        self.conversation_transcriber.session_stopped.connect(self.conversation_transcriber_session_stopped_cb)
        self.conversation_transcriber.canceled.connect(self.conversation_transcriber_recognition_canceled_cb)
        # stop transcribing on either session stopped or canceled events
        self.conversation_transcriber.session_stopped.connect(self.stop_cb)
        self.conversation_transcriber.canceled.connect(self.stop_cb)
        
    def download_convert_file(self, url):
        """
        Downloads a file from the given URL and convert it to a WAV (pcm) file.
        """
        # Generate a unique filename using current timestamp and a UUID
        filename = self.filename or f"./{int(time.time())}_{uuid.uuid4()}.wav"
        # if not os.path.exists(filename):
        #     response = requests.get(url)
        #     with open(filename, 'wb') as file:
        #         file.write(response.content)
        
        # Convert the file to WAV PCM format
        sound = AudioSegment.from_file(filename)
        sound.export(filename, format="wav")
        return filename
            
    def conversation_transcriber_recognition_canceled_cb(self, evt: speechsdk.SessionEventArgs):
        logger.info('Canceled event')

    def conversation_transcriber_session_stopped_cb(self, evt: speechsdk.SessionEventArgs):
        logger.info('SessionStopped event')

    def conversation_transcriber_transcribed_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        logger.info(f"TRANSCRIBED: {evt.result.text} {evt.result.speaker_id}")
        self.result.append({
            "text": evt.result.text, 
            "speakerId": evt.result.speaker_id,
            "speakerName": evt.result.speaker_id,
        })

    def conversation_transcriber_session_started_cb(self, evt: speechsdk.SessionEventArgs):
        logger.info('SessionStarted event')
        
    def stop_cb(self, evt: speechsdk.SessionEventArgs):
        #"""callback that signals to stop continuous recognition upon receiving an event `evt`"""
        logger.info('CLOSING on {}'.format(evt))
        self.transcribing_stop = True
        
        
    def clean_up(self):
        # Remove the downloaded file
        if os.path.exists(self.filename):
            os.remove(self.filename)
            logger.info(f"Diarization Clean up: remove file: {self.filename}")
        
    def recognize(self) -> {}:
        try:
            self.conversation_transcriber.start_transcribing_async()
            while not self.transcribing_stop:
                time.sleep(.5)
            self.conversation_transcriber.stop_transcribing_async()
            return self.result
            
        except Exception as e:
            logger.error(f"Error Diarization: {e}")
        finally:
            self.clean_up()


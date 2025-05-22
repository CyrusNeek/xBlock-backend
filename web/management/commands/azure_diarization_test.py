import azure.cognitiveservices.speech as speechsdk
import time
import json
from django.conf import settings
import requests
from pydub import AudioSegment
from django.core.management.base import BaseCommand, CommandError

def do(url):

    def download_file(url, destination):
        """
        Downloads a file from the given URL to a local destination file.
        """
        response = requests.get(url)
        with open(destination, 'wb') as file:
            file.write(response.content)
            
    def convert_audio_to_wav(input_file, output_file):
        sound = AudioSegment.from_file(input_file)
        sound.export(output_file, format="wav")
        
    def conversation_transcriber_recognition_canceled_cb(evt: speechsdk.SessionEventArgs):
        print('Canceled event')

    def conversation_transcriber_session_stopped_cb(evt: speechsdk.SessionEventArgs):
        print('SessionStopped event')

    def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        print('TRANSCRIBED:')
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print('\tText={}'.format(evt.result.text))
            print('\tSpeaker ID={}'.format(evt.result.speaker_id))
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))

    def conversation_transcriber_session_started_cb(evt: speechsdk.SessionEventArgs):
        print('SessionStarted event')

    def recognize_from_file():
        # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
        speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SUBSCRIPTION_KEY, 
            region=settings.AZURE_SERVICE_REGION)
        speech_config.speech_recognition_language="en-US"

        audio_config = speechsdk.audio.AudioConfig(filename="./test.wav")
        conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

        transcribing_stop = False

        def stop_cb(evt: speechsdk.SessionEventArgs):
            #"""callback that signals to stop continuous recognition upon receiving an event `evt`"""
            print('CLOSING on {}'.format(evt))
            nonlocal transcribing_stop
            transcribing_stop = True

        # Connect callbacks to the events fired by the conversation transcriber
        conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)
        conversation_transcriber.session_started.connect(conversation_transcriber_session_started_cb)
        conversation_transcriber.session_stopped.connect(conversation_transcriber_session_stopped_cb)
        # conversation_transcriber.canceled.connect(conversation_transcriber_recognition_canceled_cb)
        # stop transcribing on either session stopped or canceled events
        conversation_transcriber.session_stopped.connect(stop_cb)
        conversation_transcriber.canceled.connect(stop_cb)
        print("开始！！")
        conversation_transcriber.start_transcribing_async()

        # Waits for completion.
        while not transcribing_stop:
            time.sleep(.5)

        conversation_transcriber.stop_transcribing_async()


    try:
        download_file(url, "./raw_audio_test.wav")  # Download the file before processing
        convert_audio_to_wav("./raw_audio_test.wav", "./test.wav")
        recognize_from_file()
    except Exception as err:
        print("Encountered exception. {}".format(err))
        
class Command(BaseCommand):
    """This file just meant for test if azure sdk diarization work or not"""
    
    def handle(self, *args, **options):
        uri = "https://xblock-hub.s3.amazonaws.com/meetings/Butcher_and_The_Boar_Yiqiu_129.wav?AWSAccessKeyId=AKIAZIOEQ44O2QUSYNUZ&Signature=COz7O%2BX6rPbLdS2OJHIKwuyatU4%3D&Expires=1710605477"
        do(uri)
        
# if __name__ == "__main__":
#     do("https://xblock-hub.s3.amazonaws.com/meetings/Butcher_and_The_Boar_Yiqiu_129.wav?AWSAccessKeyId=AKIAZIOEQ44O2QUSYNUZ&Signature=COz7O%2BX6rPbLdS2OJHIKwuyatU4%3D&Expires=1710605477")

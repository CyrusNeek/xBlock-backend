from django.conf import settings
from openai import OpenAI
import openai

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIRunService:

    @staticmethod
    def create_run(thread_id, assistant_id):
        return client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            tools=[{"type": "file_search"}],
            model="gpt-4o.1",
        )
    
    @staticmethod
    def retrieve_run(thread_id, run_id):
        return client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            
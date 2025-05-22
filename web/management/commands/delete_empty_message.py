from django.core.management.base import BaseCommand
from web.models import LLMChat  # Adjust 'myapp' to the name of your actual app
import json
import time 

class Command(BaseCommand):
    help = "Delete empty chat messages that have empty data key"

    def handle(self, *args, **kwargs):
        llm_chats = LLMChat.objects.all()
        
        for chat in llm_chats:
            # Deserialize the JSON string into a Python dict
            messages = json.loads(chat.messages)
            
            # Check if 'data' exists and is a list
            if not messages or not messages.get('data'):
                chat.delete()
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted LLMChat id {chat.id}'))
                time.sleep(0.2)

from django.core.management.base import BaseCommand
from web.models import LLMChat  # Adjust 'myapp' to the name of your actual app
import json
import time 

class Command(BaseCommand):
    help = 'Reverse the order of messages in the data key for all LLMChat instances'

    def handle(self, *args, **kwargs):
        llm_chats = LLMChat.objects.all()
        
        for chat in llm_chats:
            # Deserialize the JSON string into a Python dict
            messages = json.loads(chat.messages)
            
            # Check if 'data' exists and is a list
            if 'data' in messages and isinstance(messages['data'], list):
                # Reverse the list
                messages['data'].reverse()
                # Serialize the modified messages dict back into a JSON string
                chat.messages = json.dumps(messages)
                
                # Save the modified chat instance to the database
                chat.save()
                
                self.stdout.write(self.style.SUCCESS(f'Successfully reversed messages for LLMChat id {chat.id}'))
                time.sleep(0.3)

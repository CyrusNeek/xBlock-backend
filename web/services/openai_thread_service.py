import openai
from openai.types.beta import Thread

class OpenAIThreadService:

    def create_thread()-> Thread:
        try:
            response = openai.beta.threads.create()
            return response
        
        except Exception as e:
            print(f"Error creating thread: {e}")
            return None
        
    @staticmethod
    def delete_thread(thread_id: str) -> bool:
        try:
            openai.beta.threads.delete(thread_id)
            return True
        
        except Exception as e:
            print(f"Error deleting thread: {e}")
            return False
        

    @staticmethod
    def create_message_in_thread(thread_id: str ,message: str,context: dict = {}, file_ids = []) :
        try:
            attachments = [{"file_id": file_id, "tools": [{"type": "file_search"}]} for file_id in file_ids]
            assistant_instruction = (
            "If the user asks about meetings, search for relevant information in the attached files. "
            "Use file_search to find meeting notes, transcripts, or discussions before responding."
            "if user asked for meeting , give data of recorded meeting first "
        )
            response = openai.beta.threads.messages.create(
                thread_id=thread_id,
                role="user", 
                content=message if not context else context.get("content", message),  
                attachments=attachments,
                metadata={"instruction": assistant_instruction}  

            )
            
            return response
            
        except Exception as e:
            print(f"Error creating message in thread: {e}")
            return None
        

    @staticmethod
    def get_thread_messages(thread_id: str):
        try:
            response = openai.beta.threads.messages.list(thread_id)
            
            messages = []
            for msg in response.data:
                messages.append({
                    "id": msg.id,
                    "role": msg.role, 
                    "content": msg.content[0].text.value if msg.content else "",
                    "created_at": msg.created_at,
                })

            return messages
        
        except Exception as e:
            print(f"Error retrieving thread messages: {e}")
            return None
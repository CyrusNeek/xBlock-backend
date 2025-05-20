import openai
import os
from .openai_data_types import FileObject 
from .file_service import FileService

class OpenAIFileService:

    @staticmethod
    def upload_file(file_path: str, purpose: str = "assistants") -> FileObject :
        if not FileService.check_file_exist(file_path):
            return None
       
        try:
            file_response = openai.files.create(
                file=open(file_path, "rb"),
                purpose=purpose
            )
            return file_response  
        except Exception as e:
            return None  
        
        
    @staticmethod
    def delete_file(file_id: str) -> bool:
        try:
            openai.files.delete(file_id)
            return True
        except Exception as e:
            print(e)
            return False
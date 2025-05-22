import openai
from openai.types.beta import VectorStore, Thread, Assistant
from .openai_vectore_store_service import OpenAIVectoreStoreService
from .openai_file_service import OpenAIFileService
from .openai_thread_service import OpenAIThreadService
from .openai_data_types import FileObject 
from .openai_assistant_service import OpenAIAssistantService
from .openai_run_service import OpenAIRunService

class OpenAIService:

    @staticmethod
    def create_run(thread_id, assistant_id):
        return OpenAIRunService.create_run(thread_id, assistant_id)
    
    @staticmethod
    def retrieve_run(thread_id, run_id):
        return OpenAIRunService.retrieve_run(thread_id, run_id)

    @staticmethod
    def create_assistant(name, description, metadata : dict ) -> Assistant :
        return OpenAIAssistantService.create_assistant(name, description, metadata)

    @staticmethod
    def create_thread() -> Thread :
        return OpenAIThreadService.create_thread()
    
    @staticmethod
    def create_message_in_thread(thread_id: str ,message: str,context: dict = {}, file_ids: list = []) :
        return OpenAIThreadService.create_message_in_thread(thread_id,message,context,file_ids)
    
    @staticmethod
    def get_thread_messages(thread_id):
        return OpenAIThreadService.get_thread_messages(thread_id)

    @staticmethod
    def delete_thread(thread_id) -> bool :
        return OpenAIThreadService.delete_thread(thread_id)

    @staticmethod
    def upload_file(file_path)-> FileObject:
        return OpenAIFileService.upload_file(file_path)

    @staticmethod
    def delete_file(file_id) -> bool:
        return OpenAIFileService.delete_file(file_id)
    

    @staticmethod
    def create_vector_store(name, description="") -> VectorStore :
        return OpenAIVectoreStoreService.create_vector_store(name, description)
    
    @staticmethod
    def delete_vector_store(vector_store_id: str) -> bool:
        return OpenAIVectoreStoreService.delete_vector_store(vector_store_id)

    
    @staticmethod
    def attach_file_to_vector_store(vector_store_id: str, file_id: str) -> bool:
        return OpenAIVectoreStoreService.attach_file_to_vector_store(vector_store_id, file_id)
    
    @staticmethod
    def remove_file_from_vector_store(vector_store_id: str, file_id: str) -> bool:
        return OpenAIVectoreStoreService.remove_file_from_vector_store(vector_store_id, file_id)
    
    @staticmethod 
    def update_assistant_vectore_store(assistant_id, vectore_store_id):
        return OpenAIAssistantService.update_assistant_vectore_store(assistant_id, vectore_store_id)
        
        
    

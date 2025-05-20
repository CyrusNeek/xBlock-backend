import openai
from openai.types.beta import VectorStore

class OpenAIVectoreStoreService:
    
    @staticmethod
    def create_vector_store(name, description="") -> VectorStore :
        response = openai.beta.vector_stores.create(
            name=name,
            metadata={"description": description } ,
            # ttl_seconds=ttl_seconds
              # Optional metadata
        )
        
        return response
    
    @staticmethod
    def delete_vector_store(vector_store_id: str) -> bool:
        try:
            openai.beta.vector_stores.delete(
                vector_store_id=vector_store_id
            )
            return True  
        except Exception as e:
            return False 

    
    @staticmethod
    def attach_file_to_vector_store(vector_store_id: str, file_id: str) -> bool:
        try:
            openai.beta.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
            return True  
        except Exception as e:
            return False 
        
    @staticmethod
    def remove_file_from_vector_store(vector_store_id: str, file_id: str) -> bool:
        try:
            openai.beta.vector_stores.files.delete(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
            return True
        except Exception as e:
            print(f"Error removing file from vector store: {e}")
            return False
        
        
    

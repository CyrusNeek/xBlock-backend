import openai
from openai.types.beta import Assistant

class OpenAIAssistantService:

    @staticmethod
    def create_assistant(name: str, description: str = "", metadata: dict = {} , model = "gpt-4o.1") -> Assistant:
        try:
            response = openai.beta.assistants.create(
                name=name,
                description=description,
                metadata=metadata,
                model=model ,
                tools=[{"type": "file_search"}]
            )
            return response
        except Exception as e:
            print(f"Error creating assistant: {e}")
            return None
        
    @staticmethod
    def update_assistant_vectore_store(assistant_id , vectore_store_id):
        assistant = openai.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vectore_store_id]}},
    )

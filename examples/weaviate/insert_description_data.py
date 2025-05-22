import json
from web.services.weaviate import WeaviateManager
from openai import OpenAI
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

weaviate_manager = WeaviateManager()
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_description_from_json(json_data):
    prompt = (
        "You are a data analysis expert specializing in interpreting structured data formats. "
        "You will be provided with various JSON files that may contain a wide range of data extracted from documents such as sales data, and more.\n\n"
        "Your task is to generate concise, accurate descriptions of the JSON files, encapsulating all essential information without inferring details that are not explicitly present.\n\n"
        "Important Guidelines:\n\n"
        "*Prioritize accuracy: If any detail within the JSON file is unclear or incomplete, state 'Unknown' instead of making assumptions.\n"
        "*Avoid hallucinations: Do not add information that is not directly supported by the JSON file.\n"
        "*Be specific: Use precise language to describe data types, values, structures, and relationships within the JSON file.\n"
        "*Date Specification: Explicitly identify and define the date(s) mentioned within the JSON file, ensuring they are accurately represented in the description.\n"
        "*Consider context: If the JSON file includes metadata or contextual information, incorporate that into your description."
        "*User field: If there is JSON for the field user, ypu only have access to first and last name, email, and phone number in your description, ignore fileds user ID and brand and do not add it or mention it into description."
    )
    
    completion = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"Create a description full of contents of the JSON data: {json.dumps(json_data)}"}
        ]
    )
    
    return completion.choices[0].message.content

def insert_description_to_collections():
    collections = weaviate_manager.collections
    for collection in collections:
        print(f"Processing collection: {collection}")
        try:
            collection_obj = weaviate_manager.get_collection(collection)
                        
            for obj in collection_obj.iterator():
                uuid = obj.uuid
                properties = obj.properties
                description = obj.properties.ai_description
                if description == None:    
                    # json_data = json.loads(json.dumps(properties, cls=DjangoJSONEncoder))
                    
                    # description = generate_description_from_json(json_data)

                    # collection_obj.data.update(
                    #     uuid=uuid,
                    #     properties={"description": description}
                    # )
                    
                    # print(f"Updated object {uuid} in collection {collection} with new description.")
                    pass
                else:
                    continue
        
        except Exception as e:
            print(f"An error occurred while processing collection {collection}: {e}")

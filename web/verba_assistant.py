from django.conf import settings

import requests
import websockets
import json
import asyncio
from web.models.openai_file import OpenAIFile

import base64

from web.services.storage_service import StorageService


upload_document_template = {"data":[{"filename":"test.json","extension":"json","content":"FILE_BASE_64"}],"textValues":[]}



def file_to_base64(file_path):
    with open(file_path, 'rb') as file:
        file_content = file.read()
        base64_content = base64.b64encode(file_content).decode('utf-8')
    return base64_content

def process_files(file_list: list[OpenAIFile]):
    result = []
    for file in file_list:
        file_path = file.file_name

        try:
            base64_content = file_to_base64(file_path)
            filename = file_path.split('/')[-1]
            extension = filename.split('.')[-1] if '.' in filename else ''
            result.append({
                'filename': filename,
                'extension': extension,
                'content': base64_content,
            })
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    return result



class VerbaAssistant:
    def __init__(self):
        self.api_url = settings.VERBA_API_URL
        self.api_ws_url = settings.VERBA_API_WEBSOCKET
        self.username = settings.VERBA_USERNAME
        self.password = settings.VERBA_PASSWORD
        self.client = requests.Session()
        self.client.auth = (self.username, self.password)
    
    def query_documents(self, query: str):
        res = self.client.post(self.api_url + "/query", json={'query': query})

        assert res.ok is True, "Response status must be ok " + res.text

        return res.json()['context']


    def upload_document(self, files: list[OpenAIFile]):
        storage_service = StorageService()

        for file in files:
            storage_service.upload_file(file.file_name, 'uploads/' + file.file_name)

        # data = process_files(files)

        # upload_document_template["data"] = data
        # config = self.client.get(self.api_url + "/config").json()['data']
        # upload_document_template['config'] = config

        # res = self.client.post(self.api_url + "/import", json=upload_document_template)

        # assert res.ok is True, "Response status must be ok " + res.text

        # print(res.text)


    async def generate_response(self, payload):
        uri = f"{self.api_ws_url}/ws/generate_stream"

        full_response = {"message": "", "finish_reason": "", "full_text": ""}
        credentials = f"{self.username}:{self.password}"
        auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"


        try:
            async with websockets.connect(uri, extra_headers={"Authorization": auth_header}) as websocket:
                await websocket.send(json.dumps(payload))
                async for message in websocket:
                    chunk = json.loads(message)
                    full_response["message"] = chunk.get("message", "")
                    full_response["finish_reason"] = chunk.get("finish_reason", "")
                    full_response["full_text"] += chunk.get("message", "")
                    
                    if chunk.get("finish_reason") == "stop":
                        break
        except Exception as e:
            full_response["message"] = str(e)
            full_response["finish_reason"] = "error"
            full_response["full_text"] = str(e)
        
        return full_response
    
    def response_sync(self, context, query, previous_conversation=None):        
      
        response = asyncio.run(self.generate_response({ "context": context, "query": query, "conversation": previous_conversation or [] }))
        
        print(response)
        return response

    





    
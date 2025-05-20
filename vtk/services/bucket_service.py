import requests
from web.services.storage_service import StorageService
import base64
from io import BytesIO

def upload_file_to_gcs(presigned_url,data, file_object):
    """
    Upload a file to Google Cloud Storage using a presigned URL and a file object.
    
    :param presigned_url: The presigned URL for uploading.
    :param file_object: The file object to upload (e.g., from `request.FILES`).
    """
    
    file_object.seek(0)

    files = {'file': file_object}

    response = requests.post(presigned_url, data=data, files=files)

    if response.status_code == 204:
        print("File uploaded successfully!")
        return True
    else:
        print(f"Failed to upload file. Status code: {response.status_code}")
        return False
    

def get_presigned_post_url(file_name):
        presigned_post = StorageService().generate_presigned_upload_url(file_name)
        return presigned_post


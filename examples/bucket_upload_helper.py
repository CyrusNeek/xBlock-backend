from web.services.google_bucket import GoogleBucket
import logging
import os
import json

logger = logging.getLogger(__name__)

def upload_data_in_bucket(item_pk, data, app_name, model_name):
    google_bucket = GoogleBucket()
    directory = f"temporary_uploads/bucket_data/{app_name}/{model_name}/"

    try:
        os.makedirs(directory, exist_ok=True)
        file_name = f"{model_name}_{item_pk}.json"
        file_path = os.path.join(directory, file_name)

        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        bucket_path = f"{app_name}/{model_name}/data/{file_name}"
        google_bucket.upload_or_replace(source=file_path, destination=bucket_path)

        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.error(f"Error uploading {model_name} (ID {item_pk}) to GCP: {e}")

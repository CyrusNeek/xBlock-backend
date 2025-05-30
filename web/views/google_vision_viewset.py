import os
import base64
import json
import tempfile
from google.cloud import vision
import re

# For local development, GOOGLE_APPLICATION_CREDENTIALS can be set to the path of a service account key JSON file.
# In Cloud Run, this variable should generally be UNSET. The Google Cloud client libraries will
# automatically use the runtime service account of the Cloud Run service if this variable is not set.
# Ensure the Cloud Run service's runtime service account has the necessary IAM permissions for Google Vision API.
credential_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if credential_path:
    # If GOOGLE_APPLICATION_CREDENTIALS is set (e.g., for local development), use it.
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path
    # print(f"Using GOOGLE_APPLICATION_CREDENTIALS: {credential_path}") # Optional: for debugging
elif not os.getenv('K_SERVICE'):
    # If not in Cloud Run (K_SERVICE is not set) and GOOGLE_APPLICATION_CREDENTIALS is not set,
    # fallback to a default local credential file for convenience during local development.
    # This part is optional and depends on your local development setup preference.
    local_fallback_credential_path = 'xbrain_credential.json'
    if os.path.exists(local_fallback_credential_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_fallback_credential_path
        # print(f"Using local fallback GOOGLE_APPLICATION_CREDENTIALS: {local_fallback_credential_path}") # Optional: for debugging
    # else:
        # print("GOOGLE_APPLICATION_CREDENTIALS not set and local fallback not found.") # Optional: for debugging
# else:
    # print("Running in Cloud Run or similar environment, expecting runtime service account to be used.") # Optional: for debugging

WORD = re.compile(r"\w+")
PROJECT_ID = "xbrain-422617"
LOCATION = "us-central1" 
MODEL_NAME = "gemini-1.0-pro-vision"

def process_image(base64_image):
    if ',' in base64_image:
        base64_image = base64_image.split(',')[1]

    image_content = base64.b64decode(base64_image)
    return vision.Image(content=image_content)

def detect_image_text(base64_image):
    client = vision.ImageAnnotatorClient()
    image = process_image(base64_image)

    response = client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(f"Vision API Error: {response.error.message}")

    texts = response.text_annotations
    if not texts:
        print("No text detected in the image.")
        return []

    ocr_text = [f"{text.description}" for text in texts]
    return ocr_text

def detect_image_content(base64_image):
    client = vision.ImageAnnotatorClient()
    image = process_image(base64_image)

    response = client.label_detection(image=image)

    if response.error.message:
        raise Exception(f"Vision API Error: {response.error.message}")

    labels = response.label_annotations
    if not labels:
        print("No labels detected in the image.")
        return []

    label_descriptions = [label.description for label in labels]
    return label_descriptions
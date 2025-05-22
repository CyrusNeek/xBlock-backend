import os
import base64
import json
import tempfile
from google.cloud import vision
import re

# Handle Google credentials from environment variable if available
gcp_credentials_json = os.getenv('GCP_CREDENTIALS')
if gcp_credentials_json:
    # Create a temporary file with the credentials
    fd, temp_path = tempfile.mkstemp(suffix='.json')
    with os.fdopen(fd, 'w') as tmp:
        tmp.write(gcp_credentials_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
else:
    # Fallback for local development
    credential_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'xbrain_credential.json')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path
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
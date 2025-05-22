import base64
import json
import nltk
import docx
import fitz
from openai import OpenAI
from pypdf import PdfReader
from django.conf import settings
from django.utils import timezone
from transformers import pipeline
from web.services.weaviate import WeaviateManager

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class ImageProcessor:
    def __init__(self, manager: WeaviateManager):
        self.manager = manager

    def upload_to_weaviate(self, page, xref, filename, description, unit_file_pk):
        return self.manager.create_object(
            "unitFileImage",
            {
                "image": base64.b64encode(open(filename, "rb").read()).decode(),
                "unitfile": unit_file_pk,
                "unitfile_name": filename,
                "page": page,
                "date": timezone.now(),
                "xref": xref,
                "description": description,
            },
        )

    def get_image_description_from_llm(self, file_path: str):
        file = client.files.create(file=open(file_path, "rb"), purpose="fine-tune")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical image analysis expert. You will be provided with various types of images extracted from documents like research papers, technical blogs, and more.\nYour task is to generate concise, accurate descriptions of the images without adding any information you are not confident about.\nFocus on capturing the key details, trends, or relationships depicted in the image.",
                },
                {
                    "role": "user",
                    "content": f"Create a description full of contents of the file {file.id} so it can be indexed properly in a vector store",
                },
            ],
        )

        return completion.choices[0].message.content

    def process_document(
        self,
        file_path: str,
        unit_name: str,
        unit_file_pk: int,
    ):
        doc = fitz.open(file_path)

        for i in range(len(doc)):
            for img in doc.get_page_images(i):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)

                filename = f"{unit_name}-{unit_name}-page-{i}-xref-{xref}.png"

                if pix.n < 5:
                    pix.save(filename)
                else:
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    pix1.save(filename)
                    pix1 = None

                pix = None

                description = self.get_image_description_from_llm(filename)

                self.upload_to_weaviate(i, xref, filename, description, unit_file_pk)

        doc.close()


class TextProcessor:
    CHUNK_SIZE = 1000
    OVERLAP = 200
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self, chunk_size=None, overlap=None, embedding_model=None):
        self.chunk_size = chunk_size if chunk_size is not None else self.CHUNK_SIZE
        self.overlap = overlap if overlap is not None else self.OVERLAP
        self.embedder = pipeline(
            "feature-extraction",
            model=embedding_model if embedding_model else self.EMBEDDING_MODEL,
        )

    def split_into_chunks(self, text):
        """
        Split text into chunks of the specified size with optional overlap.
        """
        nltk.download("punkt")
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.overlap):
            chunk = text[i : i + self.chunk_size]
            if len(chunk) > 0:
                chunks.append(chunk)
        return chunks

    def generate_embeddings(self, chunks):
        """
        Generate embeddings for each chunk.
        """
        embeddings = [self.embedder(chunk)[0] for chunk in chunks]
        return embeddings

    @classmethod
    def process_pdf(cls, file_path, chunk_size=None, overlap=None):
        """
        Process PDF file: extract text, chunk it, and generate embeddings.
        """
        processor = cls(chunk_size, overlap)
        text = processor.extract_text_from_pdf(file_path)
        chunks = processor.split_into_chunks(text)
        embeddings = processor.generate_embeddings(chunks)
        return {"chunks": chunks, "embeddings": embeddings}

    def extract_text_from_pdf(self, file_path):
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text

    @classmethod
    def process_word(cls, file_path, chunk_size=None, overlap=None):
        """
        Process Word file: extract text, chunk it, and generate embeddings.
        """
        processor = cls(chunk_size, overlap)
        text = processor.extract_text_from_word(file_path)
        chunks = processor.split_into_chunks(text)
        embeddings = processor.generate_embeddings(chunks)
        return {"chunks": chunks, "embeddings": embeddings}

    def extract_text_from_word(self, file_path):
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    @classmethod
    def process_json(cls, file_path, chunk_size=None, overlap=None):
        """
        Process JSON file: extract text, chunk it, and generate embeddings.
        """
        processor = cls(chunk_size, overlap)
        text = processor.extract_text_from_json(file_path)
        chunks = processor.split_into_chunks(text)
        embeddings = processor.generate_embeddings(chunks)
        return {"chunks": chunks, "embeddings": embeddings}

    def extract_text_from_json(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
        text = json.dumps(data)
        return text

    @staticmethod
    def save_to_file(data, output_file="output_data.json"):
        """
        Save chunks and embeddings to a JSON file.
        """
        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)

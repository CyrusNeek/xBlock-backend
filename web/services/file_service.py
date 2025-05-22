import os
from fpdf import FPDF
import uuid 
import tempfile


class FileService:

    @staticmethod
    def create_pdf_from_text(text , file_name=""):
        """Creates a PDF with the given text, using a UUID in the file name. returns file path """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in text.splitlines():
            pdf.multi_cell(0, 10, txt=line)

        if file_name != "":
            file_name = file_name + ".pdf"
        else:
            file_name = f"{uuid.uuid4().hex}.pdf"
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, file_name)

        pdf.output(temp_file_path, dest='F')
        return temp_file_path
    

    @staticmethod
    def remove_file(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")

    @staticmethod
    def check_file_exist(file_path):
        if not os.path.exists(file_path):
            print(f"Error: The file '{file_path}' does not exist.")
            return None
        return True
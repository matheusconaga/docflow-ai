from pathlib import Path

from app.ai.parsing.docx_parser import DOCXParser
from app.ai.parsing.image_parser import ImageParser
from app.ai.parsing.pdf_parser import PDFParser


# MODULE RESPONSIBLE FOR EXTRACTING TEXT FROM VARIOUS FILE TYPES
class Extractor:

    @staticmethod
    def extract(file_path: str):

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":

            return PDFParser.extract_text(file_path)

        elif extension == ".docx":

            return DOCXParser.extract_text(file_path)

        elif extension in [".png", ".jpg", ".jpeg"]:

            return ImageParser.extract_text(file_path)

        raise Exception("Unsupported file type")

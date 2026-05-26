from docx import Document
from fastapi import HTTPException


# PARSING MODULE FOR DOCX FILES
class DOCXParser:
    @staticmethod
    def extract_text(file_path: str):

        try:

            doc = Document(file_path)

            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)

            return text

        except Exception as error:

            raise HTTPException(
                status_code=500,
                detail=f"Error parsing DOCX file: {str(error)}",
            )

from docx import Document

# PARSING MODULE FOR DOCX FILES
class DOCXParser:

    @staticmethod
    def extract_text(
        file_path: str
    ):

        doc = Document(file_path)

        text = "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
        )

        return text
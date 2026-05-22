from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\Familia\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)


class ImageParser:

    @staticmethod
    def extract_text(
        file_path: str
    ):

        image = Image.open(file_path)

        try:

            text = pytesseract.image_to_string(
                image,
                lang="por"
            )

        except:

            # FALLBACK
            text = pytesseract.image_to_string(
                image
            )

        return text
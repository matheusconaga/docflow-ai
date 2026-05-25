import shutil

import pytesseract
from PIL import Image

tesseract_path = shutil.which("tesseract")

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


class ImageParser:

    @staticmethod
    def extract_text(file_path: str):

        image = Image.open(file_path)

        try:

            text = pytesseract.image_to_string(image, lang="por")

        except Exception as error:

            # FALLBACK
            text = pytesseract.image_to_string(image)
            print(error)

        return text

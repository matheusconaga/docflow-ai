import fitz
from PIL import Image
import pytesseract
import shutil



tesseract_path = shutil.which("tesseract")

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


class PDFParser:

    @staticmethod
    def extract_text(
        file_path: str
    ):

        text = ""

        pdf = fitz.open(file_path)

        for page in pdf:

            page_text = page.get_text()

            # TEXT PDF
            if page_text.strip():

                text += page_text

            # SCANNED PDF 
            else:

                # HIGH RESOLUTION
                matrix = fitz.Matrix(3, 3)

                pix = page.get_pixmap(
                    matrix=matrix
                )

                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples
                )

                # GRAYSCALE
                image = image.convert("L")

                # BINARIZATION
                image = image.point(
                    lambda x: 0 if x < 140 else 255,
                    "1"
                )

                try:

                    ocr_text = (
                        pytesseract.image_to_string(
                            image,
                            lang="por"
                        )
                    )

                except:

                    ocr_text = (
                        pytesseract.image_to_string(
                            image
                        )
                    )

                text += ocr_text

        pdf.close()

        return text
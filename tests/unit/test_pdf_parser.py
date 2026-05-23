from app.ai.parsing.pdf_parser import PDFParser


def test_extract_text_from_pdf():

    text = PDFParser.extract_text(
        "tests/files/test.pdf"
    )

    assert len(text) > 0
    
def test_extract_text_from_scanner_pdf():

    text = PDFParser.extract_text(
        "tests/files/scanner.pdf"
    )

    assert len(text) > 0
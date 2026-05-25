from app.ai.parsing.docx_parser import DOCXParser


def test_extract_text_from_docx():

    text = DOCXParser.extract_text("tests/files/doc.docx")

    assert len(text) > 0

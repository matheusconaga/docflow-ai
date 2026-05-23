from app.ai.parsing.image_parser import ImageParser


def test_extract_text_from_image():

    text = ImageParser.extract_text(
        "tests/files/image.png"
    )

    assert len(text) > 0
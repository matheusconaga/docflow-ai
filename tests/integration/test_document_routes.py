def test_pdf_pipeline(upload_file, extract_document):

    upload_response = upload_file("tests/files/test.pdf", "test.pdf", "application/pdf")

    assert upload_response.status_code == 200

    document = upload_response.json()

    extract_response = extract_document(document["id"])

    assert extract_response.status_code == 200

    extracted = extract_response.json()

    assert extracted["status"] == "processed"

    assert len(extracted["extracted_text"]) > 0


def test_scanner_pdf_pipeline(upload_file, extract_document):

    upload_response = upload_file(
        "tests/files/scanner.pdf", "scanner.pdf", "application/pdf"
    )

    assert upload_response.status_code == 200

    document = upload_response.json()

    extract_response = extract_document(document["id"])

    assert extract_response.status_code == 200

    extracted = extract_response.json()

    assert extracted["status"] == "processed"

    assert len(extracted["extracted_text"]) > 0


def test_image_pipeline(upload_file, extract_document):

    upload_response = upload_file("tests/files/image.png", "image.png", "image/png")

    assert upload_response.status_code == 200

    document = upload_response.json()

    extract_response = extract_document(document["id"])

    assert extract_response.status_code == 200

    extracted = extract_response.json()

    assert extracted["status"] == "processed"

    assert len(extracted["extracted_text"]) > 0


def test_docx_pipeline(upload_file, extract_document):

    upload_response = upload_file(
        "tests/files/doc.docx",
        "doc.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    assert upload_response.status_code == 200

    document = upload_response.json()

    extract_response = extract_document(document["id"])

    assert extract_response.status_code == 200

    extracted = extract_response.json()

    assert extracted["status"] == "processed"

    assert len(extracted["extracted_text"]) > 0

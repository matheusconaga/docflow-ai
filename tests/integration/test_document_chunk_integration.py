from unittest.mock import patch

from app.models.document import Document
from app.models.document_structured import DocumentStructured


@patch("app.services.document_structured_service.DocumentStructurer.structure")
def test_document_chunk_flow(
    mock_structure,
    client,
    db_session,
):

    document = Document(
        filename="lesson-plan.pdf",
        stored_filename="lesson-plan.pdf",
        file_path="/tmp/lesson-plan.pdf",
        status="processed",
        extracted_text="Texto pedagógico extraído",
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    mock_structure.return_value = {
        "subject": "Educação Física",
        "level": "2º Ano",
        "contents": ["Danças populares"],
        "skills": [
            {"code": "EF12EF13", "description": "Experimentar diferentes danças"}
        ],
        "methodologies": ["Atividades práticas"],
        "assessment": ["Participação dos alunos"],
    }

    # STRUCTURE
    structure_response = client.post(f"/documents/{document.id}/structure")

    assert structure_response.status_code == 200

    # CHUNK
    chunk_response = client.post(f"/documents/{document.id}/chunk")

    assert chunk_response.status_code == 200

    data = chunk_response.json()

    assert len(data) > 0

    assert data[0]["chunk_type"] is not None

    assert data[0]["content"] is not None

    assert data[0]["structured_document_id"] is not None

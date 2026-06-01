from unittest.mock import patch


class FakeChunk:
    def __init__(self):
        self.id = "123"
        self.chunk_type = "lesson_plan"
        self.content = "Planejamento pedagógico"
        self.chunk_metadata = {
            "subject": "Educação Física",
            "level": "1º Ano",
        }


@patch("app.services.rag_service.RAGGenerator.generate")
@patch("app.services.rag_service.VectorRetriever.search")
@patch("app.services.rag_service.EmbeddingGenerator.generate")
def test_rag_query_route(
    mock_embedding,
    mock_search,
    mock_generate,
    client,
):
    mock_embedding.return_value = [0.1, 0.2, 0.3]

    mock_search.return_value = [FakeChunk()]

    mock_generate.return_value = "Plano gerado"

    response = client.post(
        "/rag/query",
        json={
            "query": "gere um plano de aula",
            "top_k": 5,
            "chunk_type": "lesson_plan",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "Plano gerado"


@patch("app.services.rag_service.VectorRetriever.search")
@patch("app.services.rag_service.EmbeddingGenerator.generate")
def test_rag_search_route(
    mock_embedding,
    mock_search,
    client,
):
    mock_embedding.return_value = [0.1, 0.2, 0.3]

    mock_search.return_value = [FakeChunk()]

    response = client.post(
        "/rag/search",
        json={
            "query": "coordenação motora",
            "top_k": 5,
            "chunk_type": "lesson_plan",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

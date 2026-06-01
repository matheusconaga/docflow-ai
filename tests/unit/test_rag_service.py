from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.services.rag_service import RAGService
from tests.unit.test_rag_generator import FakeChunk


class FakeChunk:
    @patch("app.services.rag_service.EmbeddingGenerator.generate")
    def test_should_generate_rag_response(
        self,
        mock_embedding,
        mock_search,
        mock_generate,
        db_session,
    ):
        mock_embedding.return_value = [0.1, 0.2, 0.3]

        chunks = [FakeChunk(content="Planejamento sobre coordenação motora")]

        mock_search.return_value = chunks

        mock_generate.return_value = "Plano de aula gerado com sucesso"

        result = RAGService.query(
            db=db_session,
            query="gere um plano de aula",
            top_k=5,
            chunk_type="lesson_plan",
        )

        assert result["answer"] == "Plano de aula gerado com sucesso"
        assert len(result["sources"]) == 1

    @patch("app.services.rag_service.VectorRetriever.search")
    @patch("app.services.rag_service.EmbeddingGenerator.generate")
    def test_should_raise_404_when_no_chunks_found(
        self,
        mock_embedding,
        mock_search,
        db_session,
    ):
        mock_embedding.return_value = [0.1, 0.2, 0.3]

        mock_search.return_value = []

        with pytest.raises(HTTPException) as exc:
            RAGService.query(
                db=db_session,
                query="teste",
            )

        assert exc.value.status_code == 404
        assert exc.value.detail == "Nenhum chunk relevante encontrado para a consulta"

    @patch("app.services.rag_service.VectorRetriever.search")
    @patch("app.services.rag_service.EmbeddingGenerator.generate")
    def test_should_search_chunks(
        self,
        mock_embedding,
        mock_search,
        db_session,
    ):
        mock_embedding.return_value = [0.1, 0.2, 0.3]

        chunks = [
            FakeChunk(content="Chunk 1"),
            FakeChunk(content="Chunk 2"),
        ]

        mock_search.return_value = chunks

        result = RAGService.search(
            db=db_session,
            query="coordenação motora",
        )

        assert len(result) == 2

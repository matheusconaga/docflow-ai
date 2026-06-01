from unittest.mock import MagicMock, patch

from app.ai.rag.generator import RAGGenerator


class FakeChunk:
    def __init__(self):
        self.chunk_type = "lesson_plan"
        self.content = "Conteúdo pedagógico"
        self.chunk_metadata = {
            "subject": "Educação Física",
            "level": "1º Ano",
        }


class TestRAGGenerator:

    @patch("app.ai.rag.generator.client.models.generate_content")
    def test_should_generate_answer(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "Resposta gerada"

        mock_generate.return_value = mock_response

        chunks = [FakeChunk()]

        result = RAGGenerator.generate(
            query="gere um plano",
            chunks=chunks,
        )

        assert result == "Resposta gerada"

        mock_generate.assert_called_once()

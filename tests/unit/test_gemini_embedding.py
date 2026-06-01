from unittest.mock import MagicMock, patch

import pytest

from app.ai.embeddings.gemini_embedding import GeminiEmbedding


class TestGeminiEmbedding:

    @patch("app.ai.embeddings.gemini_embedding.client.models.embed_content")
    def test_should_generate_embedding(
        self,
        mock_embed,
    ):

        mock_response = MagicMock()

        mock_response.embeddings = [MagicMock(values=[0.1, 0.2, 0.3])]

        mock_embed.return_value = mock_response

        result = GeminiEmbedding.generate("TEXT")

        assert result == [0.1, 0.2, 0.3]

    @patch("app.ai.embeddings.gemini_embedding.client.models.embed_content")
    def test_should_raise_runtime_error_when_api_fails(
        self,
        mock_embed,
    ):

        mock_embed.side_effect = Exception("API ERROR")

        with pytest.raises(RuntimeError):

            GeminiEmbedding.generate("TEXT")

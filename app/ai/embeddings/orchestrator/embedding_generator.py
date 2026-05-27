from app.ai.embeddings.gemini_embedding import GeminiEmbedding


class EmbeddingGenerator:

    @staticmethod
    def generate(content: str):

        embedding = GeminiEmbedding.generate(content)

        return embedding

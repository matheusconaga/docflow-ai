from unittest.mock import MagicMock

from app.ai.rag.retriever import VectorRetriever


class FakeQuery:
    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def all(self):
        return ["chunk1", "chunk2"]


class FakeDB:
    def query(self, *args, **kwargs):
        return FakeQuery()


class TestVectorRetriever:

    def test_should_return_chunks(self):
        db = FakeDB()

        result = VectorRetriever.search(
            db=db,
            query_embedding=[0.1, 0.2, 0.3],
            top_k=5,
        )

        assert len(result) == 2

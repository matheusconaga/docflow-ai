from app.ai.chunking.activity_chunker import ActivityChunker
from app.ai.chunking.assessment_chunker import AssessmentChunker
from app.ai.chunking.bncc_chunker import BNCCChunker
from app.ai.chunking.insight_chunker import InsightChunker
from app.ai.chunking.lesson_plan_chunker import LessonPlanChunker
from app.ai.chunking.recommendation_chunker import RecommendationChunker


class DocumentChunker:

    @staticmethod
    def generate_all_chunks(structured_document):

        chunks = []

        chunks.extend(LessonPlanChunker.generate(structured_document))

        chunks.extend(ActivityChunker.generate(structured_document))

        chunks.extend(AssessmentChunker.generate(structured_document))

        chunks.extend(BNCCChunker.generate(structured_document))

        chunks.extend(RecommendationChunker.generate(structured_document))

        chunks.extend(InsightChunker.generate(structured_document))

        return chunks

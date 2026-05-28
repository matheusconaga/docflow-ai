from google import genai

from app.core.config import GEMINI_API_KEY
from app.models.document_chunk import DocumentChunk

client = genai.Client(api_key=GEMINI_API_KEY)

_PROMPT_TEMPLATE = """Você é um assistente especializado em planejamento pedagógico.
Use apenas o contexto abaixo para responder à pergunta com precisão e objetividade.

CONTEXTO:
{context}

PERGUNTA:
{query}

Resposta:"""


class RAGGenerator:

    @staticmethod
    def generate(query: str, chunks: list[DocumentChunk]) -> str:
        context_parts = []

        for chunk in chunks:
            metadata = chunk.chunk_metadata or {}
            subject = metadata.get("subject", "")
            level = metadata.get("level", "")

            header = f"[{chunk.chunk_type.upper()}"
            if subject:
                header += f" | {subject}"
            if level:
                header += f" | {level}"
            header += "]"

            context_parts.append(f"{header}\n{chunk.content}")

        context = "\n\n---\n\n".join(context_parts)
        prompt = _PROMPT_TEMPLATE.format(context=context, query=query)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        return response.text

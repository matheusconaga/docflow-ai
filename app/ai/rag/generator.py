from google import genai

from app.core.config import GEMINI_API_KEY
from app.models.document_chunk import DocumentChunk

client = genai.Client(api_key=GEMINI_API_KEY)

_STRICT_PROMPT = """Você é um assistente especializado em planejamento pedagógico.
Use apenas o contexto abaixo para responder à pergunta com precisão e objetividade.
Se o contexto não contiver informações suficientes, diga que não há dados disponíveis nos documentos.

CONTEXTO:
{context}

PERGUNTA:
{query}

Resposta:"""

_GENERATE_PROMPT = """Você é um especialista em educação brasileira e planejamento pedagógico.

REFERÊNCIA PEDAGÓGICA (extraída dos documentos do professor):
{context}

Use a referência acima como framework de alinhamento à BNCC, metodologias e contexto pedagógico.
Combine-a com seu conhecimento sobre o tema específico para gerar um conteúdo completo, detalhado e educacionalmente rico.

SOLICITAÇÃO:
{query}

Gere o conteúdo de forma profissional, estruturada e pronta para uso em sala de aula."""


class RAGGenerator:

    @staticmethod
    def generate(query: str, chunks: list[DocumentChunk], mode: str = "strict") -> str:
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
        template = _GENERATE_PROMPT if mode == "generate" else _STRICT_PROMPT
        prompt = template.format(context=context, query=query)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        return response.text

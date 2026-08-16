from google import genai
from app.core.config import GEMINI_API_KEY
from app.models.document_chunk import DocumentChunk
from app.models.class_model import ClassModel

client = genai.Client(api_key=GEMINI_API_KEY)

_ACTIVITY_PROMPT_TEMPLATE = """
Você é um especialista em pedagogia, avaliação educacional e design instrucional.
Seu objetivo é gerar uma Atividade/Avaliação profissional, bem estruturada e rigorosa.

DADOS DA ATIVIDADE:
- Turma: {class_name} ({class_grade})
- Disciplina: {subject}
- Tópico Principal: {topic}
- Tipo de Atividade: {activity_type}
- Dificuldade: {difficulty}
- Quantidade de Questões: {questions_count}

BASE DE CONHECIMENTO (Extraído dos documentos do professor):
{context}

INSTRUÇÕES DE FORMATAÇÃO:
Você DEVE retornar um JSON contendo uma lista de questões.
Crie exatamente {questions_count} questões. As questões podem mesclar múltipla escolha e respostas dissertativas, de acordo com o tópico e a dificuldade ({difficulty}).
Todas as questões DEVEM ser baseadas RIGOROSAMENTE nos conceitos presentes na Base de Conhecimento fornecida acima.

O JSON deve seguir EXATAMENTE esta estrutura:
{{
  "questions": [
    {{
      "type": "multiple_choice",
      "text": "O enunciado da questão aqui. Pode conter formatação Markdown simples se necessário.",
      "options": [
        "Alternativa 1",
        "Alternativa 2",
        "Alternativa 3",
        "Alternativa 4"
      ],
      "correct_answer": "Alternativa Correta Escrita Exatamente Igual a uma das Opções",
      "explanation": "A justificativa ou critério de correção para o professor."
    }},
    {{
      "type": "essay",
      "text": "O enunciado da questão dissertativa aqui.",
      "correct_answer": "A resposta esperada em formato de texto descritivo.",
      "explanation": "O critério de avaliação para o professor dar nota."
    }}
  ]
}}
"""

class ActivityGenerator:
    @staticmethod
    def generate(
        class_obj: ClassModel,
        subject: str,
        topic: str,
        activity_type: str,
        difficulty: str,
        questions_count: int,
        chunks: list[DocumentChunk]
    ) -> str:
        
        context_parts = []
        for chunk in chunks:
            header = f"[{chunk.chunk_type.upper()}]"
            context_parts.append(f"{header}\n{chunk.content}")
            
        context_text = "\n\n".join(context_parts)
        if not context_text.strip():
            context_text = "Nenhum material de apoio específico foi fornecido. Crie com base no seu conhecimento geral sobre o tema para esta faixa etária."
            
        prompt = _ACTIVITY_PROMPT_TEMPLATE.format(
            class_name=class_obj.name,
            class_grade=class_obj.grade,
            subject=subject,
            topic=topic,
            activity_type=activity_type,
            difficulty=difficulty,
            questions_count=questions_count,
            context=context_text
        )
        # Chamada ao modelo Gemini exigindo JSON
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        return response.text

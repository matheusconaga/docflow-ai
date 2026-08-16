from google import genai
from app.core.config import GEMINI_API_KEY
from app.models.document_chunk import DocumentChunk
from app.models.class_model import ClassModel

client = genai.Client(api_key=GEMINI_API_KEY)

_LESSON_PLAN_PROMPT_TEMPLATE = """
Você é um especialista em pedagogia e planejamento educacional.
Seu objetivo é gerar um Plano de Aula profissional, dinâmico e detalhado em formato Markdown.

DADOS DA TURMA:
- Turma: {class_name} ({class_grade})
- Disciplina: {subject}
- Alunos: {students_count}
- Tópico da Aula: {topic}
- Duração Prevista: {duration}
- Objetivos de Aprendizagem: {objectives}

CONFIGURAÇÃO DA AULA:
- Metodologias: {methodologies}
- Recursos: {resources}
- Necessidades Especiais/Atenção: {special_needs}

BASE DE CONHECIMENTO (Extraído dos documentos do professor):
{context}

INSTRUÇÕES DE FORMATAÇÃO:
Escreva o plano de aula no estilo Markdown, dividido nas seguintes seções:
1. **Introdução e Engajamento** (Como iniciar a aula e captar a atenção)
2. **Desenvolvimento do Conteúdo** (A explicação passo a passo, usando a base de conhecimento)
3. **Aplicação Prática** (Atividades usando as metodologias e recursos escolhidos)
4. **Avaliação / Fechamento** (Como medir se os alunos atingiram os objetivos)
5. **Adaptações e Acessibilidade** (Dicas para os alunos com necessidades especiais)

IMPORTANTE:
- Seja prático e direto.
- Utilize ativamente as metodologias selecionadas.
- Se o professor passou uma Base de Conhecimento, incorpore os conceitos e diretrizes dela na aula.
"""

class LessonPlanGenerator:
    @staticmethod
    def generate(
        class_obj: ClassModel,
        subject: str,
        topic: str,
        objectives: str,
        duration: str,
        methodologies: list[str],
        resources: list[str],
        special_needs: str,
        chunks: list[DocumentChunk]
    ) -> str:
        
        context_parts = []
        for chunk in chunks:
            header = f"[{chunk.chunk_type.upper()}]"
            context_parts.append(f"{header}\n{chunk.content}")
            
        context = "\n\n---\n\n".join(context_parts) if context_parts else "Nenhum documento adicional fornecido. Baseie-se no seu conhecimento geral."
        
        methodologies_str = ", ".join(methodologies) if methodologies else "Nenhuma selecionada"
        resources_str = ", ".join(resources) if resources else "Quadro e Giz"
        special_needs_str = special_needs if special_needs else "Nenhuma necessidade especial reportada"

        prompt = _LESSON_PLAN_PROMPT_TEMPLATE.format(
            class_name=class_obj.name,
            class_grade=class_obj.grade,
            subject=subject,
            students_count=class_obj.students_count,
            topic=topic,
            duration=duration,
            objectives=objectives,
            methodologies=methodologies_str,
            resources=resources_str,
            special_needs=special_needs_str,
            context=context
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
        )

        return response.text

import json
import google.generativeai as genai
from typing import Dict, Any

_GRADER_PROMPT = """
Você é um professor corrigindo as respostas dissertativas de um aluno.
Abaixo estão as perguntas, o que o aluno respondeu, a resposta esperada e os critérios de correção.
Sua tarefa é avaliar as respostas, dar uma nota de 0 a 100 para cada uma delas, e fornecer um feedback geral construtivo para o aluno.

Você DEVE retornar um JSON estrito seguindo o formato:
{{
  "essay_scores": {{
    "0": 80,
    "1": 100
  }},
  "general_feedback": "Muito bem! Você compreendeu a maioria dos conceitos. Na questão sobre ..., tente elaborar mais sobre ..."
}}

IMPORTANTE: 
- O campo "essay_scores" deve conter como chave o NÚMERO DO ÍNDICE da questão, e como valor a nota de 0 a 100 daquela questão.
- O campo "general_feedback" deve ser encorajador e apontar onde o aluno errou, mas sem ser rude. Diga algo como "Excelente prova, mas atenção no conceito X".

DADOS DA AVALIAÇÃO:
{questions_data}
"""

class AutoGrader:
    @staticmethod
    def grade(structured_content: Dict[str, Any], student_answers: Dict[str, str]) -> Dict[str, Any]:
        questions = structured_content.get("questions", [])
        if not questions:
            return {"score": 0.0, "feedback": "Não foi possível corrigir a prova, questões não encontradas."}

        total_questions = len(questions)
        weight_per_question = 10.0 / total_questions
        
        final_score = 0.0
        
        essay_data_to_grade = []
        
        # Correção automática e separação das dissertativas
        for idx, q in enumerate(questions):
            student_ans = student_answers.get(str(idx), "")
            
            if q.get("type") == "multiple_choice":
                correct_ans = q.get("correct_answer", "")
                if student_ans.strip().lower() == correct_ans.strip().lower():
                    final_score += weight_per_question
            elif q.get("type") == "essay":
                essay_data_to_grade.append({
                    "index": idx,
                    "question_text": q.get("text", ""),
                    "expected_answer": q.get("correct_answer", ""),
                    "explanation_criteria": q.get("explanation", ""),
                    "student_answer": student_ans
                })

        # Se houver dissertativas, chama a IA
        general_feedback = "Prova objetiva corrigida automaticamente. Excelente trabalho!"
        
        if essay_data_to_grade:
            prompt = _GRADER_PROMPT.format(questions_data=json.dumps(essay_data_to_grade, ensure_ascii=False, indent=2))
            
            try:
                client = genai.GenerativeModel("gemini-3.1-flash-lite")
                response = client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                    )
                )
                
                ai_result = json.loads(response.text)
                
                essay_scores = ai_result.get("essay_scores", {})
                for str_idx, score_100 in essay_scores.items():
                    # score_100 é de 0 a 100. weight_per_question é o peso real na prova (ex: 2.5 pontos)
                    earned_points = (float(score_100) / 100.0) * weight_per_question
                    final_score += earned_points
                    
                general_feedback = ai_result.get("general_feedback", "Sua prova foi analisada pelo sistema.")
            except Exception as e:
                print(f"AutoGrader AI Error: {e}")
                general_feedback = "Houve um erro ao processar o feedback automático das questões dissertativas."

        return {
            "score": round(final_score, 1),
            "feedback": general_feedback
        }

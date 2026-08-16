import json
import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.class_model import ClassModel
from app.models.student_model import StudentModel
from app.models.activity import Activity
from app.models.activity_submission import ActivitySubmission

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])

class TrendData(BaseModel):
    name: str # e.g. "Jan", "Fev"
    performance: int # 0-100
    engagement: int # 0-100
    completion: int # 0-100

class Insight(BaseModel):
    title: str
    description: str
    type: str # "positive", "alert", "neutral"
    action: str
    action_url: str

class StudentRisk(BaseModel):
    id: str
    name: str
    class_id: str
    class_name: str
    average: float
    trend: str # "caindo", "estável", "subindo"

class IntelligenceResponse(BaseModel):
    trendData: List[TrendData]
    insights: List[Insight]
    studentsAtRisk: List[StudentRisk]

_INSIGHTS_PROMPT = """
Você é um Coordenador Pedagógico e Analista de Dados de uma escola de alto nível.
Sua missão é olhar para os dados de desempenho (notas), engajamento (taxa de participação) e conclusão (entregas) das turmas deste professor nos últimos meses e gerar 3 Conselhos Práticos (Insights).

Aqui estão os dados agregados dos últimos meses e a performance mensal dos alunos na escala 0-100:
{trend_data}

Diretrizes para os Insights:
1. Seja analítico: identifique quedas de nota, picos de engajamento ou padrões.
2. Seja propositivo e prático na "description".
3. DICA IMPORTANTE: Se houver "0" nos meses mais antigos, significa apenas que a turma não usava o sistema ainda. Não seja dramático nem critique meses antigos sem dados. Fale apenas das tendências recentes.
4. O campo "action" deve OBRIGATORIAMENTE ser o rótulo de um botão muito curto (MÁXIMO 4 PALAVRAS). (Ex: 'Gerar Plano de Revisão', 'Aplicar Atividade', 'Ver Turmas').
5. O campo "action_url" OBRIGATORIAMENTE deve ser um dos 3 links do nosso sistema que mais se adeque à ação:
   - "/professor/ensino/planos/gerar" (Se a ação sugerir criar um Plano de Aula/Revisão)
   - "/professor/ensino/atividades/gerar" (Se a ação sugerir criar uma Nova Atividade/Prova)
   - "/professor/turmas" (Se a ação sugerir analisar alunos ou ver turmas)

Responda OBRIGATORIAMENTE no formato JSON abaixo, sem usar formatação Markdown de bloco de código (` ```json `).
Retorne apenas a lista (array) e nada mais:
[
  {{
    "title": "Título atrativo e direto do insight",
    "description": "Explicação detalhada da tendência recente observada.",
    "type": "positive", // Use "positive", "alert", ou "neutral"
    "action": "Botão curto de até 4 palavras (ex: 'Gerar Plano')",
    "action_url": "/professor/ensino/planos/gerar"
  }},
  ...
]
"""

# Global in-memory cache to save AI tokens: 
# Key: MD5 hash of trend_data, Value: {"insights": List[Insight], "timestamp": datetime}
_INSIGHTS_CACHE = {}

@router.get("/insights", response_model=IntelligenceResponse)
def get_intelligence_insights(
    class_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Base query for classes
    classes_query = db.query(ClassModel).filter(
        ClassModel.teacher_id == current_user.id,
        ClassModel.is_deleted == False
    )
    if class_id and class_id != "all":
        classes_query = classes_query.filter(ClassModel.id == class_id)
        
    classes = classes_query.all()
    if not classes:
        return IntelligenceResponse(trendData=[], insights=[], studentsAtRisk=[])
        
    class_ids = [c.id for c in classes]
    class_names = {c.id: c.name for c in classes}
    
    # Get students
    students = db.query(StudentModel).filter(StudentModel.class_id.in_(class_ids)).all()
    student_map = {s.id: s for s in students}
    total_students = len(students)
    
    # Get activities
    activities = db.query(Activity).filter(Activity.class_id.in_(class_ids), Activity.is_deleted == False).all()
    activity_ids = [a.id for a in activities]
    
    # Get submissions for last 6 months
    # Manual month subtraction
    now = datetime.utcnow()
    past_month = now.month - 5
    past_year = now.year
    if past_month <= 0:
        past_month += 12
        past_year -= 1
        
    # First day of the month 5 months ago
    six_months_ago = datetime(past_year, past_month, 1)
    
    submissions = []
    if activity_ids:
        submissions = db.query(ActivitySubmission).filter(
            ActivitySubmission.activity_id.in_(activity_ids),
            ActivitySubmission.status == "reviewed",
            ActivitySubmission.submitted_at >= six_months_ago
        ).all()

    # Calculate trends by month
    months_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    
    # Create the last 6 months buckets
    trend_buckets = []
    for i in range(5, -1, -1):
        m = now.month - i
        y = now.year
        if m <= 0:
            m += 12
            y -= 1
        trend_buckets.append({
            "year": y,
            "month": m,
            "name": months_labels[m - 1],
            "scores": [],
            "expected_submissions": 0,
            "actual_submissions": 0
        })

    # Distribute activities and submissions to buckets
    for act in activities:
        if act.created_at >= six_months_ago:
            for b in trend_buckets:
                if b["year"] == act.created_at.year and b["month"] == act.created_at.month:
                    # Expected submissions = number of students in that class
                    class_student_count = len([s for s in students if s.class_id == act.class_id])
                    b["expected_submissions"] += class_student_count
                    
    for sub in submissions:
        for b in trend_buckets:
            if b["year"] == sub.submitted_at.year and b["month"] == sub.submitted_at.month:
                b["actual_submissions"] += 1
                if sub.final_score is not None:
                    b["scores"].append(sub.final_score)

    trend_data = []
    month_idx = 0
    for b in trend_buckets:
        avg_score = sum(b["scores"]) / len(b["scores"]) if b["scores"] else 0
        perf = int(avg_score * 10) # 0-10 -> 0-100
        
        engagement = 0
        if b["expected_submissions"] > 0:
            engagement = int((b["actual_submissions"] / b["expected_submissions"]) * 100)
            
        # [Simulate downward trend for demo if the user requested it]
        # Current month index: 'i' from the outer loop was just an offset. Let's make oldest=highest, newest=lowest.
        # We'll artificially drop engagement by 15% per month to force a negative trend.
        engagement = max(10, 95 - (month_idx * 15))
        
        # Mock completion as a slight variation of engagement for demo purposes
        completion = min(100, engagement + (perf % 5))
        
        trend_data.append(TrendData(
            name=b["name"],
            performance=perf,
            engagement=engagement,
            completion=completion
        ))
        
        month_idx += 1

    # Calculate students at risk
    student_grades = {s.id: [] for s in students}
    for sub in submissions:
        if sub.final_score is not None:
            student_grades[sub.student_id].append(sub.final_score)
            
    students_at_risk = []
    for sid, grades in student_grades.items():
        if grades:
            avg = sum(grades) / len(grades)
            if avg < 6.0: # Below 6 is considered at risk
                student = student_map[sid]
                # Determine trend (compare last grade with average)
                trend = "estável"
                if len(grades) > 1:
                    if grades[-1] < avg:
                        trend = "caindo"
                    elif grades[-1] > avg:
                        trend = "subindo"
                        
                students_at_risk.append(StudentRisk(
                    id=student.id,
                    name=student.name,
                    class_id=student.class_id,
                    class_name=class_names.get(student.class_id, ""),
                    average=round(avg, 1),
                    trend=trend
                ))
    
    # Sort at risk by lowest average
    students_at_risk.sort(key=lambda x: x.average)
    students_at_risk = students_at_risk[:5] # Top 5 at risk
    
    # Generate insights via Gemini
    insights = []
    try:
        # Serialize trend to string
        trend_str = json.dumps([t.model_dump() for t in trend_data], indent=2)
        # Append "v4" to the string to invalidate the old cache to generate correct action_url
        trend_hash = hashlib.md5((trend_str + "_v4").encode("utf-8")).hexdigest()
        
        # Check cache
        cache_entry = _INSIGHTS_CACHE.get(trend_hash)
        if cache_entry:
            # Optionally check expiration here (e.g. 24h), but since the hash checks
            # the exact trend data, it naturally updates when new grades come in.
            insights = cache_entry["insights"]
        else:
            model = genai.GenerativeModel("gemini-3.1-flash-lite")
            
            response = model.generate_content(
                _INSIGHTS_PROMPT.format(trend_data=trend_str),
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            
            insights_data = json.loads(response.text)
            for indata in insights_data:
                insights.append(Insight(**indata))
                
            # Store in cache
            _INSIGHTS_CACHE[trend_hash] = {
                "insights": insights,
                "timestamp": datetime.utcnow()
            }
            
    except Exception as e:
        print(f"Error generating insights: {e}")
        # Fallback insights
        insights = [
            Insight(
                title="Atenção aos Alunos em Risco",
                description=f"Há {len(students_at_risk)} alunos precisando de atenção especial nesta turma.",
                type="alert",
                action="Revise os conceitos base com esses alunos."
            ),
            Insight(
                title="Análise em Andamento",
                description="Continue avaliando os alunos para gerar insights mais precisos no próximo mês.",
                type="neutral",
                action="Gere e corrija mais atividades."
            )
        ]

    return IntelligenceResponse(
        trendData=trend_data,
        insights=insights,
        studentsAtRisk=students_at_risk
    )

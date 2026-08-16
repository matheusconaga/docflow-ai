from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import time

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.class_model import ClassModel
from app.models.document_chunk import DocumentChunk
from app.models.document_structured import DocumentStructured
from app.models.document import Document as DBDocument
from app.models.activity import Activity
from app.models.activity_submission import ActivitySubmission
from app.models.student_model import StudentModel
from app.models.lesson_plan_template import LessonPlanTemplate
from fastapi.responses import StreamingResponse
from jinja2 import Template
import markdown
import html
import re
import json
from htmldocx import HtmlToDocx
import io
from docx import Document as DocxDocument
from app.ai.rag.auto_grader import AutoGrader

from app.ai.embeddings.gemini_embedding import GeminiEmbedding
from app.ai.rag.activity_generator import ActivityGenerator

router = APIRouter(prefix="/activities", tags=["activities"])

class ActivityGenerateRequest(BaseModel):
    classId: str
    subject: str
    topic: str
    activityType: str
    difficulty: str
    questionsCount: int

class ActivityResponse(BaseModel):
    id: str
    class_id: str
    title: str
    activity_type: str
    topic: str
    difficulty: str
    questions_count: int
    generated_content: str
    structured_content: Optional[dict] = None
    created_at: str

class ActivityPublicResponse(BaseModel):
    id: str
    title: str
    activity_type: str
    topic: str
    questions_count: int
    class_name: str
    class_grade: str
    structured_content: Optional[dict] = None

class ActivitySubmitRequest(BaseModel):
    student_id: str
    answers: dict

class ActivitySubmissionResponse(BaseModel):
    id: str
    student_id: str
    student_name: str
    answers: dict
    ai_score: Optional[float]
    ai_feedback: Optional[str]
    final_score: Optional[float]
    final_feedback: Optional[str]
    status: str
    submitted_at: str

class ActivityApproveRequest(BaseModel):
    final_score: float
    final_feedback: str

class ActivityExportRequest(BaseModel):
    template_id: str

@router.post("/generate", response_model=ActivityResponse)
def generate_activity(
    data: ActivityGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.ai_credits <= 0:
        raise HTTPException(status_code=403, detail="Créditos insuficientes. Faça upgrade do seu plano para continuar gerando conteúdo.")

    # 1. Verifica se a turma existe e pertence ao professor
    class_obj = db.query(ClassModel).filter(
        ClassModel.id == data.classId,
        ClassModel.teacher_id == current_user.id
    ).first()

    if not class_obj:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
        
    if class_obj.is_locked:
        raise HTTPException(status_code=403, detail="Esta turma está bloqueada devido ao limite do seu plano atual. Faça upgrade para gerar conteúdo para ela.")

    # 2. Busca RAG: Obter os embeddings do tópico e buscar contextos
    query = f"{data.subject} - {data.topic}. {data.activityType} nível {data.difficulty}"
    query_embedding = GeminiEmbedding.generate(query)

    chunks = db.query(DocumentChunk).join(
        DocumentStructured, DocumentChunk.structured_document_id == DocumentStructured.id
    ).join(
        DBDocument, DocumentStructured.document_id == DBDocument.id
    ).filter(
        DBDocument.teacher_id == current_user.id,
        DocumentChunk.embedding.isnot(None)
    ).order_by(
        DocumentChunk.embedding.l2_distance(query_embedding)
    ).limit(5).all()

    # 3. Gerar a Avaliação com Gemini
    generated_json_text = ActivityGenerator.generate(
        class_obj=class_obj,
        subject=data.subject,
        topic=data.topic,
        activity_type=data.activityType,
        difficulty=data.difficulty,
        questions_count=data.questionsCount,
        chunks=chunks
    )

    try:
        structured_content = json.loads(generated_json_text)
    except json.JSONDecodeError:
        structured_content = None

    # 4. Salvar no Banco
    title = f"{data.activityType} de {data.subject} - {data.topic}"
    activity = Activity(
        teacher_id=current_user.id,
        class_id=data.classId,
        title=title,
        activity_type=data.activityType,
        topic=data.topic,
        difficulty=data.difficulty,
        questions_count=data.questionsCount,
        generated_content=generated_json_text, # backup/raw
        structured_content=structured_content
    )
    
    db.add(activity)
    
    # 5. Descontar crédito
    current_user.ai_credits -= 1
    
    db.commit()
    db.refresh(activity)

    return ActivityResponse(
        id=activity.id,
        class_id=activity.class_id,
        title=activity.title,
        activity_type=activity.activity_type,
        topic=activity.topic,
        difficulty=activity.difficulty,
        questions_count=activity.questions_count,
        generated_content=activity.generated_content,
        structured_content=activity.structured_content,
        created_at=activity.created_at.isoformat()
    )

@router.get("/", response_model=List[ActivityResponse])
def list_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    activities = db.query(Activity).filter(
        Activity.teacher_id == current_user.id,
        Activity.is_deleted == False
    ).order_by(Activity.created_at.desc()).all()
    
    return [
        ActivityResponse(
            id=act.id,
            class_id=act.class_id,
            title=act.title,
            activity_type=act.activity_type,
            topic=act.topic,
            difficulty=act.difficulty,
            questions_count=act.questions_count,
            generated_content=act.generated_content,
            structured_content=act.structured_content,
            created_at=act.created_at.isoformat()
        ) for act in activities
    ]

@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    act = db.query(Activity).filter(
        Activity.id == activity_id,
        Activity.teacher_id == current_user.id,
        Activity.is_deleted == False
    ).first()
    
    if not act:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
        
    return ActivityResponse(
        id=act.id,
        class_id=act.class_id,
        title=act.title,
        activity_type=act.activity_type,
        topic=act.topic,
        difficulty=act.difficulty,
        questions_count=act.questions_count,
        generated_content=act.generated_content,
        structured_content=act.structured_content,
        created_at=act.created_at.isoformat()
    )

@router.delete("/{activity_id}")
def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    act = db.query(Activity).filter(
        Activity.id == activity_id,
        Activity.teacher_id == current_user.id
    ).first()
    
    if not act:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
        
    act.is_deleted = True
    db.commit()
    
    return {"status": "success"}

@router.get("/public/{activity_id}", response_model=ActivityPublicResponse)
def get_public_activity(
    activity_id: str,
    db: Session = Depends(get_db)
):
    act = db.query(Activity).filter(
        Activity.id == activity_id,
        Activity.is_deleted == False
    ).first()
    
    if not act:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
        
    class_obj = db.query(ClassModel).filter(ClassModel.id == act.class_id).first()
    
    # Sanitiza o JSON para não enviar a resposta correta e a explicação pro aluno
    public_structured = None
    if act.structured_content and "questions" in act.structured_content:
        import copy
        public_structured = copy.deepcopy(act.structured_content)
        for q in public_structured["questions"]:
            q.pop("correct_answer", None)
            q.pop("explanation", None)
            
    return ActivityPublicResponse(
        id=act.id,
        title=act.title,
        activity_type=act.activity_type,
        topic=act.topic,
        questions_count=act.questions_count,
        class_name=class_obj.name if class_obj else "",
        class_grade=class_obj.grade if class_obj else "",
        structured_content=public_structured
    )

@router.get("/public/{activity_id}/students")
def get_public_activity_students(
    activity_id: str,
    db: Session = Depends(get_db)
):
    act = db.query(Activity).filter(Activity.id == activity_id, Activity.is_deleted == False).first()
    if not act:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
        
    submitted_student_ids = [sub.student_id for sub in db.query(ActivitySubmission).filter(ActivitySubmission.activity_id == activity_id).all()]
    
    students = db.query(StudentModel).filter(
        StudentModel.class_id == act.class_id,
        StudentModel.is_deleted == False
    ).all()
    
    available_students = [{"id": s.id, "name": s.name} for s in students if s.id not in submitted_student_ids]
    return available_students

@router.post("/public/{activity_id}/submit")
def submit_public_activity(
    activity_id: str,
    data: ActivitySubmitRequest,
    db: Session = Depends(get_db)
):
    act = db.query(Activity).filter(Activity.id == activity_id, Activity.is_deleted == False).first()
    if not act:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
        
    existing_sub = db.query(ActivitySubmission).filter(
        ActivitySubmission.activity_id == activity_id,
        ActivitySubmission.student_id == data.student_id
    ).first()
    if existing_sub:
        raise HTTPException(status_code=400, detail="Você já enviou esta prova.")

    # Correção automática
    grade_result = AutoGrader.grade(act.structured_content or {}, data.answers)
    
    submission = ActivitySubmission(
        activity_id=activity_id,
        student_id=data.student_id,
        answers=data.answers,
        ai_score=grade_result["score"],
        ai_feedback=grade_result["feedback"],
        status="pending_review"
    )
    
    db.add(submission)
    db.commit()
    return {"status": "success", "message": "Prova entregue com sucesso"}

@router.get("/{activity_id}/submissions", response_model=List[ActivitySubmissionResponse])
def get_activity_submissions(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify owner
    act = db.query(Activity).filter(Activity.id == activity_id, Activity.teacher_id == current_user.id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
        
    submissions = db.query(ActivitySubmission).filter(ActivitySubmission.activity_id == activity_id).all()
    
    result = []
    for sub in submissions:
        student = db.query(StudentModel).filter(StudentModel.id == sub.student_id).first()
        result.append(ActivitySubmissionResponse(
            id=sub.id,
            student_id=sub.student_id,
            student_name=student.name if student else "Desconhecido",
            answers=sub.answers,
            ai_score=sub.ai_score,
            ai_feedback=sub.ai_feedback,
            final_score=sub.final_score,
            final_feedback=sub.final_feedback,
            status=sub.status,
            submitted_at=sub.submitted_at.isoformat()
        ))
    return result

@router.put("/submissions/{sub_id}/approve")
def approve_submission(
    sub_id: str,
    data: ActivityApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(ActivitySubmission).filter(ActivitySubmission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
        
    act = db.query(Activity).filter(Activity.id == sub.activity_id, Activity.teacher_id == current_user.id).first()
    if not act:
        raise HTTPException(status_code=403, detail="Acesso negado")
        
    sub.final_score = data.final_score
    sub.final_feedback = data.final_feedback
    sub.status = "reviewed"
    db.commit()
    
    return {"status": "success"}

@router.post("/{activity_id}/export")
def export_activity(
    activity_id: str,
    data: ActivityExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    act = db.query(Activity).filter(
        Activity.id == activity_id,
        Activity.teacher_id == current_user.id,
        Activity.is_deleted == False
    ).first()
    
    if not act:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
        
    template = db.query(LessonPlanTemplate).filter(
        LessonPlanTemplate.id == data.template_id,
        LessonPlanTemplate.teacher_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
        
    class_obj = db.query(ClassModel).filter(ClassModel.id == act.class_id).first()
        
    try:
        html_template_string = template.html_content
        
        def clean_jinja_tags(match):
            inner = match.group(1)
            inner_no_tags = re.sub(r'<[^>]*>', '', inner)
            inner_unescaped = html.unescape(inner_no_tags)
            inner_clean = inner_unescaped.replace('\xa0', ' ').strip()
            return f"{{{{ {inner_clean} }}}}"
            
        sanitized_html = re.sub(r'\{\{(.*?)\}\}', clean_jinja_tags, html_template_string)
        
        jinja_template = Template(sanitized_html)
        
        # Build Markdown from structured_content if available, otherwise fallback
        if act.structured_content and "questions" in act.structured_content:
            md_parts = [f"# {act.title}\n\n"]
            for i, q in enumerate(act.structured_content["questions"]):
                md_parts.append(f"### {i+1}. {q.get('text', '')}")
                if q.get("type") == "multiple_choice":
                    for opt in q.get("options", []):
                        md_parts.append(f"- [ ] {opt}")
                md_parts.append("\n")
            
            md_parts.append("\n---\n## Gabarito\n")
            for i, q in enumerate(act.structured_content["questions"]):
                md_parts.append(f"**{i+1}.** {q.get('correct_answer', '')} _({q.get('explanation', '')})_\n")
            
            content_html = markdown.markdown("\n".join(md_parts))
        else:
            content_html = markdown.markdown(act.generated_content)
        
        context = {
            "title": act.title,
            "type": act.activity_type,
            "topic": act.topic,
            "difficulty": act.difficulty,
            "questions_count": act.questions_count,
            "class_name": class_obj.name if class_obj else "",
            "class_grade": class_obj.grade if class_obj else "",
            "content": content_html,
            "subject": act.title.split("-")[0].replace("Prova de", "").replace("Exercício de", "").strip() if "-" in act.title else act.title,
            "duration": "N/A",
            "scope": "Avaliação"
        }
        
        final_html = jinja_template.render(**context)
        final_html = final_html.replace('\n', '')
        
        doc = DocxDocument()
        parser = HtmlToDocx()
        parser.add_html_to_document(final_html, doc)
        
        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        
        return StreamingResponse(
            output_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="atividade_{act.id}.docx"'
            }
        )
    except Exception as e:
        print(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao exportar: {str(e)}")

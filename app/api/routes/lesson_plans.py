from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
import io
import markdown
import re
import html
from docx import Document
from htmldocx import HtmlToDocx
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from jinja2 import Template
import time

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.class_model import ClassModel
from app.models.document_chunk import DocumentChunk
from app.models.document_structured import DocumentStructured
from app.models.document import Document
from app.models.lesson_plan import LessonPlan
from app.models.lesson_plan_template import LessonPlanTemplate

from app.ai.embeddings.gemini_embedding import GeminiEmbedding
from app.ai.rag.lesson_plan_generator import LessonPlanGenerator

router = APIRouter(prefix="/lesson-plans", tags=["lesson_plans"])

class LessonPlanGenerateRequest(BaseModel):
    classId: str
    subject: str
    topic: str
    objectives: str
    duration: str
    scope: str
    template: str
    methodologies: List[str]
    resources: List[str]
    specialNeeds: str

class LessonPlanUpdateRequest(BaseModel):
    content: str

class ExportRequest(BaseModel):
    template_id: str

class LessonPlanResponse(BaseModel):
    id: str
    class_id: str
    subject: str
    topic: str
    objectives: str
    duration: str
    scope: str
    template: str
    methodologies: List[str]
    resources: List[str]
    special_needs: Optional[str]
    generated_content: str
    created_at: str

    class Config:
        from_attributes = True

@router.post("/generate", response_model=LessonPlanResponse)
def generate_and_save_lesson_plan(
    data: LessonPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Obter a turma
    class_obj = db.query(ClassModel).filter(
        ClassModel.id == data.classId,
        ClassModel.teacher_id == current_user.id,
        ClassModel.is_deleted == False
    ).first()
    
    if not class_obj:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    # 2. Busca RAG: Obter os embeddings do tópico e buscar contextos
    query = f"{data.subject} - {data.topic}. {data.objectives}"
    query_embedding = GeminiEmbedding.generate(query)

    chunks = db.query(DocumentChunk).join(
        DocumentStructured, DocumentChunk.structured_document_id == DocumentStructured.id
    ).join(
        Document, DocumentStructured.document_id == Document.id
    ).filter(
        Document.teacher_id == current_user.id,
        DocumentChunk.embedding.isnot(None)
    ).order_by(
        DocumentChunk.embedding.l2_distance(query_embedding)
    ).limit(5).all()

    # 3. Gerar o Plano de Aula com Gemini
    generated_content = LessonPlanGenerator.generate(
        class_obj=class_obj,
        subject=data.subject,
        topic=data.topic,
        objectives=data.objectives,
        duration=data.duration,
        methodologies=data.methodologies,
        resources=data.resources,
        special_needs=data.specialNeeds,
        chunks=chunks
    )

    # 4. Salvar no Banco
    lesson_plan = LessonPlan(
        teacher_id=current_user.id,
        class_id=data.classId,
        subject=data.subject,
        topic=data.topic,
        objectives=data.objectives,
        duration=data.duration,
        scope=data.scope,
        template=data.template,
        methodologies=data.methodologies,
        resources=data.resources,
        special_needs=data.specialNeeds,
        generated_content=generated_content
    )
    
    db.add(lesson_plan)
    db.commit()
    db.refresh(lesson_plan)

    return LessonPlanResponse(
        id=lesson_plan.id,
        class_id=lesson_plan.class_id,
        subject=lesson_plan.subject,
        topic=lesson_plan.topic,
        objectives=lesson_plan.objectives,
        duration=lesson_plan.duration,
        scope=lesson_plan.scope,
        template=lesson_plan.template,
        methodologies=lesson_plan.methodologies,
        resources=lesson_plan.resources,
        special_needs=lesson_plan.special_needs,
        generated_content=lesson_plan.generated_content,
        created_at=lesson_plan.created_at.isoformat()
    )

@router.get("/", response_model=List[LessonPlanResponse])
def list_lesson_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plans = db.query(LessonPlan).filter(
        LessonPlan.teacher_id == current_user.id,
        LessonPlan.is_deleted == False
    ).order_by(LessonPlan.created_at.desc()).all()
    
    return [
        LessonPlanResponse(
            id=p.id,
            class_id=p.class_id,
            subject=p.subject,
            topic=p.topic,
            objectives=p.objectives,
            duration=p.duration,
            scope=p.scope,
            template=p.template,
            methodologies=p.methodologies,
            resources=p.resources,
            special_needs=p.special_needs,
            generated_content=p.generated_content,
            created_at=p.created_at.isoformat()
        ) for p in plans
    ]

@router.get("/{plan_id}", response_model=LessonPlanResponse)
def get_lesson_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(LessonPlan).filter(
        LessonPlan.id == plan_id,
        LessonPlan.teacher_id == current_user.id,
        LessonPlan.is_deleted == False
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plano de aula não encontrado")
        
    return LessonPlanResponse(
        id=plan.id,
        class_id=plan.class_id,
        subject=plan.subject,
        topic=plan.topic,
        objectives=plan.objectives,
        duration=plan.duration,
        scope=plan.scope,
        template=plan.template,
        methodologies=plan.methodologies,
        resources=plan.resources,
        special_needs=plan.special_needs,
        generated_content=plan.generated_content,
        created_at=plan.created_at.isoformat()
    )

@router.delete("/{plan_id}")
def delete_lesson_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(LessonPlan).filter(
        LessonPlan.id == plan_id,
        LessonPlan.teacher_id == current_user.id,
        LessonPlan.is_deleted == False
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plano de aula não encontrado")
        
    plan.is_deleted = True
    from datetime import datetime
    plan.deleted_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Plano de aula deletado com sucesso"}

@router.put("/{plan_id}", response_model=LessonPlanResponse)
def update_lesson_plan(
    plan_id: str,
    data: LessonPlanUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(LessonPlan).filter(
        LessonPlan.id == plan_id,
        LessonPlan.teacher_id == current_user.id,
        LessonPlan.is_deleted == False
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plano de aula não encontrado")
        
    plan.generated_content = data.content
    db.commit()
    db.refresh(plan)
    
    return LessonPlanResponse(
        id=plan.id,
        class_id=plan.class_id,
        subject=plan.subject,
        topic=plan.topic,
        objectives=plan.objectives,
        duration=plan.duration,
        scope=plan.scope,
        template=plan.template,
        methodologies=plan.methodologies,
        resources=plan.resources,
        special_needs=plan.special_needs,
        generated_content=plan.generated_content,
        created_at=plan.created_at.isoformat()
    )

@router.post("/{plan_id}/export-docx")
async def export_lesson_plan_docx(
    plan_id: str,
    data: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(LessonPlan).filter(
        LessonPlan.id == plan_id,
        LessonPlan.teacher_id == current_user.id,
        LessonPlan.is_deleted == False
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plano de aula não encontrado")
        
    template = db.query(LessonPlanTemplate).filter(
        LessonPlanTemplate.id == data.template_id,
        LessonPlanTemplate.teacher_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
        
    class_obj = db.query(ClassModel).filter(ClassModel.id == plan.class_id).first()
        
    try:
        # Pega a estrutura HTML salva do editor web
        html_template_string = template.html_content
        
        # Limpa qualquer tag HTML ou entidade (como &nbsp;) que tenha entrado nas tags Jinja {{ }}
        def clean_jinja_tags(match):
            inner = match.group(1)
            # Remove tags HTML internas (ex: {{ <strong>subject</strong> }})
            inner_no_tags = re.sub(r'<[^>]*>', '', inner)
            # Converte entidades HTML como &nbsp; ou &amp;
            inner_unescaped = html.unescape(inner_no_tags)
            # Remove espaços de não-quebra (\xa0) e limpa
            inner_clean = inner_unescaped.replace('\xa0', ' ').strip()
            return f"{{{{ {inner_clean} }}}}"
            
        sanitized_html = re.sub(r'\{\{(.*?)\}\}', clean_jinja_tags, html_template_string)
        
        jinja_template = Template(sanitized_html)
        
        # Converte o conteúdo markdown (do plano gerado) para HTML
        content_html = markdown.markdown(plan.generated_content)
        
        # Prepara o contexto com as variáveis do plano
        context = {
            "subject": plan.subject,
            "topic": plan.topic,
            "objectives": plan.objectives,
            "duration": plan.duration,
            "scope": plan.scope,
            "class_name": class_obj.name if class_obj else "",
            "class_grade": class_obj.grade if class_obj else "",
            "methodologies": ", ".join(plan.methodologies),
            "resources": ", ".join(plan.resources),
            "special_needs": plan.special_needs or "Nenhuma",
            "content": content_html,
        }
        
        # Injeta as variáveis no HTML final
        final_html = jinja_template.render(context)
        
        # Cria um novo documento docx em branco e injeta o HTML
        doc = Document()
        parser = HtmlToDocx()
        parser.add_html_to_document(final_html, doc)
        
        # Salva o resultado em memória
        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        
        return StreamingResponse(
            output_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="plano_de_aula_{plan.subject}.docx"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar o template: {str(e)}")

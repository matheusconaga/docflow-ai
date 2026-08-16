from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.class_model import ClassModel
from app.models.document import Document
from app.schemas.document_chunk_schema import DocumentChunkResponse
from app.schemas.document_embedding_schema import DocumentEmbeddingResponse
# DOCUMENTS SCHEMAS
from app.schemas.document_schema import DocumentResponse
from app.schemas.document_structured_schema import DocumentStructuredResponse
from app.schemas.extract_document_schema import ExtractDocumentResponse
from app.services.document_chunk_service import DocumentChunkService
from app.services.document_embedding_service import DocumentEmbeddingService
# DOCUMENTS SERVICES
from app.services.document_service import DocumentService
from app.services.document_structured_service import DocumentStructuredService
from app.services.extract_document_service import ExtractDocumentService
from app.ai.rag.retriever import VectorRetriever
from app.ai.rag.generator import RAGGenerator
from pydantic import BaseModel
import os

class DocumentTestRequest(BaseModel):
    query: str

class DocumentTestResponse(BaseModel):
    response: str

router = APIRouter(prefix="/documents", tags=["Documents"])


# ROUTE FOR GETTING ALL DOCUMENTS FOR THE LOGGED-IN TEACHER
@router.get("/", response_model=List[DocumentResponse])
def get_all_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = db.query(Document).filter(
        Document.teacher_id == current_user.id,
        Document.is_deleted == False
    ).order_by(Document.created_at.desc()).all()
    return documents


# ROUTE FOR GETTING ALL DOCUMENTS BY CLASS ID
@router.get("/classes/{class_id}/documents", response_model=List[DocumentResponse])
def get_class_documents(
    class_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_class = db.query(ClassModel).filter(
        ClassModel.id == class_id, 
        ClassModel.teacher_id == current_user.id
    ).first()
    
    if not db_class:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
        
    documents = db.query(Document).filter(
        Document.class_id == class_id,
        Document.is_deleted == False
    ).order_by(Document.created_at.desc()).all()
    return documents


# ROUTE FOR UPLOADING A DOCUMENT
# RECEIVES FILE, SAVES IT
# CREATES DOCUMENT RECORD
@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    class_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # If a class is specified, check if the user owns it
    if class_id:
        db_class = db.query(ClassModel).filter(
            ClassModel.id == class_id, 
            ClassModel.teacher_id == current_user.id
        ).first()
        
        if not db_class:
            raise HTTPException(status_code=404, detail="Turma não encontrada ou acesso negado")

    document = await DocumentService.upload_document(
        db=db, file=file, teacher_id=current_user.id, class_id=class_id
    )

    # Schedule the processing pipeline in the background
    background_tasks.add_task(DocumentService.process_document_pipeline, document.id, current_user.id)

    return document


# ROUTE FOR EXTRACTING TEXT
# RECEIVES DOCUMENT ID
# EXTRACTS TEXT
# UPDATES DOCUMENT RECORD
@router.post("/{document_id}/extract", response_model=(ExtractDocumentResponse))
def extract_document(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.teacher_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado ou acesso negado")

    document = ExtractDocumentService.extract_document(db=db, document_id=document_id)

    return document


# ROUTE FOR STRUCTURE EXTRACT_TEXT


@router.post("/{document_id}/structure", response_model=DocumentStructuredResponse)
def structure_document(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.teacher_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado ou acesso negado")

    return DocumentStructuredService.structure_document(db=db, document_id=document_id)


# ROUTE FOR GENERATING CHUNKS
@router.post("/{document_id}/chunk", response_model=list[DocumentChunkResponse])
def chunk_document(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.teacher_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado ou acesso negado")

    return DocumentChunkService.chunk_document(db=db, document_id=document_id)


# ROUTE FOR GENERATING EMBEDDINGS
@router.post(
    "/{document_id}/embeddings", response_model=list[DocumentEmbeddingResponse]
)
def generate_embeddings(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.teacher_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado ou acesso negado")

    return DocumentEmbeddingService.generate_embeddings(
        db=db,
        document_id=document_id,
    )

@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(
        Document.id == document_id, 
        Document.teacher_id == current_user.id,
        Document.is_deleted == False
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    # Excluir arquivo fisico
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"Erro ao deletar arquivo fisico: {e}")

    # Soft delete the document
    doc.is_deleted = True
    from datetime import datetime
    doc.deleted_at = datetime.utcnow()
    db.commit()
    return None

@router.get("/{document_id}/preview", response_model=DocumentStructuredResponse)
def preview_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.teacher_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    from app.models.document_structured import DocumentStructured
    structured = db.query(DocumentStructured).filter(DocumentStructured.document_id == document_id).first()
    if not structured:
        raise HTTPException(status_code=404, detail="Estrutura do documento ainda não processada")
        
    return structured

@router.post("/{document_id}/test", response_model=DocumentTestResponse)
def test_document(
    document_id: str,
    data: DocumentTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.teacher_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
        
    if doc.status != "processed":
        raise HTTPException(status_code=400, detail="Documento ainda não foi totalmente processado")

    # 1. Gerar embedding da pergunta
    from app.ai.embeddings.gemini_embedding import GeminiEmbedding
    query_embedding = GeminiEmbedding.generate(data.query)
    
    # 2. Buscar chunks
    from app.models.document_chunk import DocumentChunk
    from app.models.document_structured import DocumentStructured
    
    chunks = db.query(DocumentChunk).join(
        DocumentStructured, DocumentChunk.structured_document_id == DocumentStructured.id
    ).filter(
        DocumentStructured.document_id == document_id,
        DocumentChunk.embedding.isnot(None)
    ).order_by(
        DocumentChunk.embedding.cosine_distance(query_embedding)
    ).limit(5).all()
    
    if not chunks:
        return DocumentTestResponse(response="Nenhum conteúdo encontrado neste documento para responder à sua pergunta.")
        
    # 3. Gerar resposta
    answer = RAGGenerator.generate(query=data.query, chunks=chunks)
    
    return DocumentTestResponse(response=answer)

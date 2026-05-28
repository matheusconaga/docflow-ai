import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.api.routes.documents import router as documents_router
from app.api.routes.rag import router as rag_router
from app.db.database import get_db
from app.models.document_structured import DocumentStructured

app = FastAPI(
    title="DocFlow AI",
    description="API for document analysis",
    version="0.0.1",
)


# HEALTHCHECK
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/getdocuments")
def get_docs(db: Session = Depends(get_db)):
    documents = db.query(DocumentStructured).all()

    return {"data": documents}


# REGISTERED ROUTES
app.include_router(documents_router)
app.include_router(rag_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


# MIDLEWARE CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

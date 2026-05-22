from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.documents import router as documents_router

app = FastAPI(
    title="DocFlow AI",
    description="API for document analysis",
    version="0.0.1",
)


# REGISTERED ROUTES
app.include_router(documents_router)


# MIDLEWARE CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



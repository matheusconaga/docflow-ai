import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.api.routes.auth import router as auth_router
from app.api.routes.classes import router as classes_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.documents import router as documents_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.rag import router as rag_router
from app.api.routes.students import router as students_router
from app.api.routes.lesson_plans import router as lesson_plans_router
from app.api.routes.templates import router as templates_router
from app.api.routes.activities import router as activities_router
from app.api.routes.submissions import router as submissions_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.billing import router as billing_router
from app.api.routes.pre_registration import router as preregistration_router
from app.api.routes.admin import router as admin_router
from app.db.database import SessionLocal, get_db
from app.models.document_structured import DocumentStructured
from app.models.user import User  # noqa: F401 - ensure table is created
from app.models.class_model import ClassModel  # noqa: F401 - ensure table is created
from app.models.student_model import StudentModel  # noqa: F401 - ensure table is created
from app.models.lesson_plan_template import LessonPlanTemplate  # noqa: F401 - ensure table is created
from app.models.billing_history import BillingHistory  # noqa: F401 - ensure table is created
from app.models.pre_registration import PreRegistration  # noqa: F401 - ensure table is created
from app.services.auth_service import seed_admin_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed admin
    from app.db.database import Base, engine

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="EducAssist API",
    description="API for EducAssist platform",
    version="0.0.1",
    lifespan=lifespan,
)


# HEALTHCHECK
@app.get("/health")
def health():
    return {"status": "ok"}





# REGISTERED ROUTES
app.include_router(auth_router)
app.include_router(classes_router)
app.include_router(dashboard_router)
app.include_router(documents_router)
app.include_router(notifications_router)
app.include_router(rag_router)
app.include_router(students_router)
app.include_router(lesson_plans_router)
app.include_router(templates_router)
app.include_router(activities_router)
app.include_router(submissions_router, prefix="/submissions", tags=["Submissions"])
app.include_router(intelligence_router)
app.include_router(billing_router)
app.include_router(preregistration_router)
app.include_router(admin_router)

os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# MIDLEWARE CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

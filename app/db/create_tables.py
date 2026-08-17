from sqlalchemy import text

from app.db.database import Base, engine

# Import all models so SQLAlchemy registers every table
from app.models.user import User  # noqa: F401
from app.models.class_model import ClassModel  # noqa: F401
from app.models.student_model import StudentModel  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.document_chunk import DocumentChunk  # noqa: F401
from app.models.document_structured import DocumentStructured  # noqa: F401
from app.models.notification_model import NotificationModel  # noqa: F401
from app.models.lesson_plan import LessonPlan  # noqa: F401
from app.models.lesson_plan_template import LessonPlanTemplate  # noqa: F401
from app.models.activity import Activity  # noqa: F401
from app.models.activity_submission import ActivitySubmission  # noqa: F401
from app.models.billing_history import BillingHistory  # noqa: F401
from app.models.pre_registration import PreRegistration  # noqa: F401

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(bind=engine)

print("Tables created successfully.")

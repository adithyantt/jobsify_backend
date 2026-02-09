from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    user_id = Column(Integer, nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    reporter_email = Column(String, nullable=False)  # Email of the user who reported
    reason = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
